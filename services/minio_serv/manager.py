import aioboto3
from fastapi import HTTPException, UploadFile
from app.core.config import settings
from botocore.config import Config

class MinioHandler:
    def __init__(self, backet, access_key: str, secret_key: str, endpoint: str, secure=True):
        self.backet = backet
        self.session = aioboto3.Session()
        self.endpoint_url = f"{'https' if secure else 'http'}://{endpoint}"
        self.credentials = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key
        }

    async def upload_file(self, file_path: str, file: UploadFile):
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url, **self.credentials) as s3:
                await s3.upload_fileobj(file.file, self.backet, file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def get_file(self, file_name):
        """pull file MinIO"""
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url, **self.credentials) as s3:
                await s3.get_object(
                    Bucket=self.backet, Key=file_name
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"pull file failed: {str(e)}")
        
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.credentials["aws_access_key_id"],
            aws_secret_access_key=self.credentials["aws_secret_access_key"],
        ) as s3_client:
            response = await s3_client.get_object(Bucket=self.backet, Key=file_name)
            return await response['Body'].read()
    
    async def delete_file(self, file_name:str):
        """delete file MinIO"""
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url, **self.credentials) as s3:
                await s3.delete_object(
                    Bucket=self.backet, Key=file_name
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Deleted failed: {str(e)}")
        
    async def exists_file(self, file_name:str):
        """check type if exists in storage"""
        try:
            async with self.session.client("s3",
            endpoint_url=self.endpoint_url, **self.credentials) as s3:
                await s3.head_object(Bucket=self.backet, Key=file_name)
            return True
        except Exception:
            return False

minio_handler = MinioHandler(
    backet=settings.BUCKET_NAME,
    endpoint=settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    secure=settings.MINIO_SECURE,
)