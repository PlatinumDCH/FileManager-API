from fastapi import APIRouter, Depends
from minio import Minio
from app.config.client_minio import get_minio_client

router = APIRouter()

@router.post("/create-bucket/{user_id}")
async def create_user_bucket(user_id: str, minio_client: Minio = Depends(get_minio_client)):
    bucket_name = f"user-{user_id}-bucket"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        return {"message": f"Бакет '{bucket_name}' создан!"}
    
    return {"message": f"Бакет '{bucket_name}' уже существует."}

