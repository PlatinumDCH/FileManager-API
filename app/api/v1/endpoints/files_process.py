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
    print(unique_name)
    file_size = file.size if file.size is not None else 0
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    if file.size and file.size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
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
    user_id:int =  Query(...),
    file_name:str = Query(..., description='original name file'),
    session:AsyncSession = Depends(get_conn_db)
): 
    file_record = await file_manager.get_uniq_name(
        user_id=user_id,
        orig_file_name=file_name,
        session=session
    )
    if not file_record:
        raise HTTPException(
            status_code=404,
            detail='File not found'
        )
    uniq_name = file_record.file_path
    file_data = await minio_handler.get_file(uniq_name)

    file_stream = io.BytesIO(file_data)

    return StreamingResponse(
        file_stream,
        media_type='application/octet-stream',
        headers={
            "Content-Disposition":f"attachment; filename={file_name}"
        }
    )

@router.get("/list-files")
async def list_files(
    user_id: int = Query(..., description="ID user"),
    session: AsyncSession = Depends(get_conn_db),
):
    files = await file_manager.get_files_by_user(
        session=session,
        user_id=user_id
    )
    if not files:
        return {
            "message":"User dont have upload files",
            "files": []
        }
    file_list = [
        {
            "file_name": file.file_name,
            "file_path": file.file_path,
            "size": file.size,
            "uploaded_at": file.created_at
        }
        for file in files
    ]

    return {"files": file_list}