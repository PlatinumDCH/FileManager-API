from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from minio import Minio, S3Error
from app.core.client_minio import get_minio_client
from typing import cast

router = APIRouter()

@router.post("/create-bucket/{user_id}")
async def create_user_bucket(user_id: str, minio_client: Minio = Depends(get_minio_client)):
    bucket_name = f"user-{user_id}-bucket"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        return {"message": f"Бакет '{bucket_name}' создан!"}
    
    return {"message": f"Бакет '{bucket_name}' уже существует."}

@router.post('/upload-file/{user_id}')
async def upload_file(
    user_id: str,
    file: UploadFile = File(...),
    minio_client: Minio = Depends(get_minio_client)
):
    bucket_name = f'user-{user_id}-bucket'
    if not minio_client.bucket_exists(bucket_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'bucker {bucket_name} not found'
        )
    file_name = cast(str, file.filename)

    try:
        minio_client.put_object(
            bucket_name,
            file_name,
            file.file,
            length= -1,
            part_size=10*1024*1024
        )
    except S3Error as e:
        raise HTTPException(status_code=500,
                            detail='Error load fil {e}')
    return {'message':f'File {file_name} sucessfull load in backet {bucket_name}'}
