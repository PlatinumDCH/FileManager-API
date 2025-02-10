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
import uuid
from minio import Minio, S3Error

from services.minio_serv.manager import minio_handler
from app.db.crund_file import file_manager
from app.core.config import settings
from app.api.v1.dependecies.client_db import get_conn_db
from app.db.schemas import DonwloadFile

router = APIRouter(prefix="/files")


@router.post("/upload")
async def upload_file(
    user_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_conn_db),
):
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file without name or file not get",
        )

    # check access role file :todo

    file_extension = file.filename.split(".")[-1]
    unique_name = await file_manager.create_uniq_name(
        user_id=user_id, file_extesion=file_extension
    )
    
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    file_size = file.size if file.size is not None else 0

    if file_size  > MAX_SIZE:
        raise HTTPException(
            status_code=400, 
            detail="File too large"
            )

    await minio_handler.upload_file(unique_name, file)

    await file_manager.create_file(
        session=session,
        user_id=user_id,
        file_name=file.filename,
        path=unique_name,
        size=file_size,
    )

    return {"status": "uploaded", "name": file.filename}


@router.get("/download")
async def download_file(
    user_id: int = Query(...),
    file_name: str = Query(..., description="original name file"),
    session: AsyncSession = Depends(get_conn_db),
):
    file_record = await file_manager.get_uniq_name(
        user_id=user_id, orig_file_name=file_name, session=session
    )
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    uniq_name = file_record.file_path
    file_data = await minio_handler.get_file(uniq_name)

    file_stream = io.BytesIO(file_data)

    return StreamingResponse(
        file_stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )


@router.get("/list-files")
async def list_files(
    user_id: int = Query(..., description="ID user"),
    session: AsyncSession = Depends(get_conn_db),
):
    """get list file database by user"""
    files = await file_manager.get_files_by_user(session=session, user_id=user_id)
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
    user_id: int = Query(..., description="Id user"),
    file_name: str = Query(..., description="Original FileName"),
    session: AsyncSession = Depends(get_conn_db),
):
    """delete file MinIO DataBase"""
    file_object = await file_manager.get_uniq_name(
        user_id=user_id, orig_file_name=file_name, session=session
    )
    if not file_object:
        raise HTTPException(status_code=404, detail="File not found")

    uniq_name = file_object.file_path

    await minio_handler.delete_file(uniq_name)
    await file_manager.delete_file(file_object, session)

    return {
        "message": "File sucessfull deleted",
        "file_name": file_name
        }

@router.put("/update")
async def update_file(
    user_id:int = Query(..., description='Id user'),
    file_name:str = Query(..., description='Original name file'),
    new_file: UploadFile = File(...),
    session = Depends(get_conn_db)
):
    if not new_file or not new_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="file without name or file not get",
        )
    
    MAX_SIZE = 5 * 1024 * 1024  # 5MB
    file_size = new_file.size if new_file.size is not None else 0

    if file_size  > MAX_SIZE:
        raise HTTPException(
            status_code=400, 
            detail="File too large"
            )
    
    file_obj = await file_manager.get_uniq_name(
        user_id=user_id,
        orig_file_name=file_name,
        session=session,

    )
    if not file_obj:
        raise HTTPException(
            status_code=404,
            detail='File not found'
        )
    
    
    old_unique_name = file_obj.file_path
    
    await minio_handler.delete_file(old_unique_name)

    file_extension = new_file.filename.split(".")[-1]

    new_unique_name = await file_manager.create_uniq_name(
        user_id=user_id, file_extesion=file_extension
    )
    
    await minio_handler.upload_file(new_unique_name, new_file)

    update_file = await file_manager.update_file_record(
        session,
        file_obj,
        new_unique_name,
        file_size
    )
    if not update_file:
        raise HTTPException(
            status_code=500,
            detail='Failed to update file record'
        )

    return {
        "message": "file sucesfull update", 
        "new_file_path": new_unique_name}
    

@router.get("/file_exists")
async def check_file_exists(
    user_id:int = Query(..., description='User ID'),
    file_name:str = Query(..., description='Original file name'),
    session = Depends(get_conn_db)
):
    file_obj = await file_manager.get_uniq_name(
        user_id=user_id,
        orig_file_name=file_name,
        session=session
    )
    if not file_obj:
        raise HTTPException(
            status_code=404,
            detail='File not found'
        )
    exists = await minio_handler.exists_file(file_obj.file_path)

    if not exists:
        raise HTTPException(
            status_code=404,
            detail='File not found in MinIO storage'
        )
    
    return {"message":"File exists"}
