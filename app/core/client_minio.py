from minio import Minio, S3Error

from app.utils.logger import logger
from app.core.config import settings


def get_minio_client() -> Minio:
    return Minio(
    settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    secure=settings.MINIO_SECURE
)

def  ensure_bucket_exists(bucket_name: str):
    """Проверяет, существует ли бакет, и создаёт его, если нет."""
    client = get_minio_client()
    
    try:
        if not client.bucket_exists(bucket_name):
            logger.info(f"bucket '{bucket_name}' not found. creating...")
            client.make_bucket(bucket_name)
            logger.info(f"bucker '{bucket_name}' sucessful сreated.")
        else:
            logger.info(f"bucker '{bucket_name}' exist.")
    except S3Error as err:
        logger.error(f"Error  check/create backet: {err}")