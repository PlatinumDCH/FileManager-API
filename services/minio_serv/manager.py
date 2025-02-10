# import io
# import aioboto3
# from services.minio_serv.client_minio import get_minio_client
# from app.core.config import settings

# async def upload_file_minio(file_stream:io.BytesIO, file_name:str):
#     session = aioboto3.Session()

#     async with session.client(
#         's3',
#         endpoint_url=settings.MINIO_URL,
#         aws_access_key_id=settings.MINIO_ACCESS_KEY,
#         aws_secret_access_key=settings.MINIO_SECEET_KEY
#     ) as client:
#         file_stream.seek(0)

#         await client.put_object(
#             Bucket=settings.BUCKET_NAME,
#             Key = file_name,
#             Body = file_stream,
#             )

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
        async with self.session.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.credentials["aws_access_key_id"],
            aws_secret_access_key=self.credentials["aws_secret_access_key"],
        ) as s3_client:
            response = await s3_client.get_object(Bucket=self.backet, Key=file_name)
            return await response['Body'].read()
        
    # def list(self):
    #     objects = list(self.client.list_objects(self.bucket))
    #     return [{"name": i.object_name, "last_modified": i.last_modified} for i in objects]

    # def stats(self, name: str) -> minio.api.Object:
    #     return self.client.stat_object(self.bucket, name)

    # def download_file(self, name: str):
    #     info = self.client.stat_object(self.bucket, name)
    #     total_size = info.size
    #     offset = 0
    #     while True:
    #         response = self.client.get_object(self.bucket, name, offset=offset, length=2048)
    #         yield response.read()
    #         offset = offset + 2048
    #         if offset >= total_size:
    #             break


minio_handler = MinioHandler(
    backet=settings.BUCKET_NAME,
    endpoint=settings.MINIO_URL,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    secure=settings.MINIO_SECURE,
)