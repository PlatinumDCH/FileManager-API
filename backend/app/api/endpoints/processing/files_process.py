from fastapi import (
    APIRouter,
    Depends,
    File,
    Query,
    UploadFile,
    HTTPException,
    status,
    UploadFile,
    File,
    status,
)
import io
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.minio_serv.manager import minio_handler
from backend.app.repository.manager import crud
from backend.app.core.config import settings
from backend.app.api.dependecies.security import AuthService
from backend.app.api.dependecies.client_db import get_conn_db
from backend.app.api.dependecies.validate_file import FileExtensionValidator
from backend.app.api.dependecies.validate_file import get_file_extension_validator

router = APIRouter(prefix="/files")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_conn_db),
    auth_user=Depends(AuthService().get_current_user),
    file_extesions_validator: FileExtensionValidator = Depends(
        get_file_extension_validator
    ),
):
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file without name or file received",
        )

    try:
        file_type = await file_extesions_validator.validate(file.filename)
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=f'Unsupported file extension for file "{file.filename}"',
        )

    try:
        unique_name = await crud.files.generate_uniq_filename(
            user_id=auth_user.id, file=file, file_type=file_type
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error generating unique filename : {str(e)}",
        )

    file_size = file.size if file.size is not None else 0

    if file_size > settings.MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    await minio_handler.upload_file(unique_name, file)

    await crud.files.create_file(
        session=session,
        user_id=auth_user.id,
        file_name=file.filename,
        file_path=unique_name,
        size=file_size,
    )

    return {"status": "uploaded", "name": file.filename}


@router.get("/download")
async def download_file(
    file_name: str = Query(..., description="original name file"),
    session: AsyncSession = Depends(get_conn_db),
    auth_user=Depends(AuthService().get_current_user),
):
    file_object = await crud.files.get_file_record(
        user_id=auth_user.id, orig_file_name=file_name, session=session
    )
    if not file_object:
        raise HTTPException(status_code=404, detail="File not found")

    uniq_name = file_object.file_path

    file_data = await minio_handler.get_file(uniq_name)

    if file_data is None:
        raise HTTPException(status_code=404, detail="File data not found")

    file_stream = io.BytesIO(file_data)  # type:ignore

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


@router.get("/list-files")
async def list_files(
    auth_user=Depends(AuthService().get_current_user),
    session: AsyncSession = Depends(get_conn_db),
):
    """get list file database by user"""
    files = await crud.files.get_files(session=session, user_id=auth_user.id)
    if not files:
        return {"message": "User dont have upload files", "files": []}
    file_list = [
        {
            "file_name": file.file_name,
            "file_path": file.file_path,
            "size": file.size,
            "uploaded_at": file.created_at,
        }
        for file in files
    ]

    return {"files": file_list}


@router.delete("/delete")
async def delete_file(
    auth_user=Depends(AuthService().get_current_user),
    file_name: str = Query(..., description="Original FileName"),
    session: AsyncSession = Depends(get_conn_db),
):
    """delete file MinIO DataBase"""
    file_object = await crud.files.get_file_record(
        user_id=auth_user.id, orig_file_name=file_name, session=session
    )
    if not file_object:
        raise HTTPException(status_code=404, detail="File not found")

    uniq_name = file_object.file_path

    await minio_handler.delete_file(uniq_name)
    await crud.files.delete_file_record(file_object, session)

    return {"message": "File sucessfull deleted", "file_name": file_name}


@router.put("/update")
async def update_file(
    auth_user=Depends(AuthService().get_current_user),
    file_name: str = Query(..., description="Original name file"),
    new_file: UploadFile = File(...),
    session=Depends(get_conn_db),
    file_extesions_validator: FileExtensionValidator = Depends(
        get_file_extension_validator
    ),
):
    if not new_file or not new_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file without name or file not get",
        )

    file_size = new_file.size if new_file.size is not None else 0

    if file_size > settings.MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    try:
        file_type = await file_extesions_validator.validate(new_file.filename)
    except HTTPException as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=f'Unsupported file extension for file "{new_file.filename}"',
        )

    file_obj = await crud.files.get_file_record(
        user_id=auth_user.id,
        orig_file_name=file_name,
        session=session,
    )
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")

    old_unique_name = file_obj.file_path

    await minio_handler.delete_file(old_unique_name)

    new_unique_name = await crud.files.generate_uniq_filename(
        user_id=auth_user.id, file=new_file, file_type=file_type
    )

    await minio_handler.upload_file(new_unique_name, new_file)

    update_file = await crud.files.update_file_record(
        session, file_obj, new_unique_name, file_size
    )
    if not update_file:
        raise HTTPException(status_code=500, detail="Failed to update file record")

    return {"message": "file sucesfull update", "new_file_path": new_unique_name}


@router.get("/file_exists")
async def check_file_exists(
    auth_user=Depends(AuthService().get_current_user),
    file_name: str = Query(..., description="Original file name"),
    session=Depends(get_conn_db),
):
    file_obj = await crud.files.get_file_record(
        user_id=auth_user.id, orig_file_name=file_name, session=session
    )
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found")
    exists = await minio_handler.exists_file(file_obj.file_path)

    if not exists:
        raise HTTPException(status_code=404, detail="File not found in MinIO storage")

    return {"message": "File exists"}
