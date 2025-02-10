from minio import Minio, S3Error

from app.utils.logger import logger
from app.core.config import settings
from contextlib import contextmanager

@contextmanager
def get_minio_client():
    client =  Minio(
        settings.MINIO_URL,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECEET_KEY,
        secure=settings.MINIO_SECURE)
    try:
        yield client
    finally:
        del client


def  ensure_bucket_exists(bucket_name: str):
    """check, if exists backer and create him if not found"""
    with get_minio_client() as client:    
        try:
            if not client.bucket_exists(bucket_name):
                logger.info(f"bucket '{bucket_name}' not found. creating...")
                client.make_bucket(bucket_name)
                logger.info(f"bucker '{bucket_name}' sucessful сreated.")
            else:
                logger.info(f"bucker '{bucket_name}' exist.")
        except S3Error as err:
            logger.error(f"Error  check/create backet: {err}")