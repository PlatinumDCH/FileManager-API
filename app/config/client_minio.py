from minio import Minio
from app.config.b_settings import settings

def get_minio_client() -> Minio:
    return Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    secure=settings.MINIO_SECURE
)