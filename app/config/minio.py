from minio import Minio
from app.config.b_settings import settings

minio_client = Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    secure=settings.MINIO_SECURE
)

def get_minio_client() -> Minio:
    return minio_client