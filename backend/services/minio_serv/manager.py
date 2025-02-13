import magic
from fastapi import HTTPException, UploadFile
from typing import Optional, BinaryIO

from backend.services.minio_serv.client import IClient, s3_client_manager
from backend.app.core.config import settings
from backend.app.utils.logger import logger

class MinioHandler:
    """
    A class to handle interactions with MinIo using the S3 client.
    """
    def __init__(
            self,
            bucket : str,
            client: IClient  
    ):
        """
        Initialize the MinioHandler with a bucket name and an S3 client manager.

        :param bucket: The name of the bucket to interact with.
        :param s3_client_manager: An instance of S3ClientManager to handle S3 client creation.
        """
        self.bucket = bucket
        self.client = client

    async def upload_file(self, file_path: str, file: UploadFile):
        """
        Upload a file to MinIO.

        :param file_path: The path where the file fill be stored in the buclet.
        :param file: Thr file to upload.
        :raices HTTPException: If the upload fails.
        """
        try:
            # mime = magic.Magic(mime=True)
            # file_type = mime.from_buffer(await file.read())

            async with await self.client.get_client() as s3:
                await s3.upload_fileobj(
                    file.file, 
                    self.bucket, 
                    file_path,
                    # ExtraArgs={'ContentType':file_type}
                )
            logger.info(f'File uploaded successfully to {file_path}')
        except Exception as e:
            logger.error(f'Upload failed: {str(e)}')
            raise HTTPException(
                status_code=500, 
                detail=f"Upload failed: {str(e)}"
            )
        
    async def get_file(self, file_name : str) ->Optional[BinaryIO]:
        """
        Retrieve a file from MinIO.

        :param file_name: The name if the file to retrieve.
        :return: The file content as a binary stream.
        :raises HTTPException: If the fuke rettieval fails.
        """
        try:
            async with await self.client.get_client() as s3:
                response = await s3.get_object(
                    Bucket=self.bucket, 
                    Key=file_name
                )
                return await response['Body'].read()
        except Exception as e:
            logger.error(f'Failed to retrive file {file_name}: {str(e)}')
            raise HTTPException(
                status_code=500, 
                detail=f"pull file failed: {str(e)}"
            )
    
    async def delete_file(self, file_name:str)->None:
        """
        Delete file_name:The name of the file to delete
        
        :param file_name: The name of the file to delete.
        :raises HTTPException: If the delection fails.
        """
        try:
            async with await self.client.get_client() as s3:
                await s3.delete_object(
                    Bucket=self.bucket, 
                    Key=file_name
                )
            logger.info(f'File {file_name} deletect successfully')
        except Exception as e:
            logger.error(f'Failed to delete file {file_name}: {str(e)}')
            raise HTTPException(
                status_code=500, 
                detail=f"Deleted failed: {str(e)}"
            )
        
    async def exists_file(self, file_name:str)->bool:
        """
        Check if type exists in MinIO
        
        :param file_name: The name of the file to check.
        :return: True if the file exests, False otherwise.
        """
        try:
            async with await self.client.get_client() as s3:
                await s3.head_object(
                    Bucket=self.bucket, 
                    Key=file_name
                )
            return True
        except Exception as e:
            logger.warning(f'File {file_name} does not exist: {str(e)}')
            return False

    async def exists_bucket(self):
        """
        create bocket in MinIO, if not exists.

        :returned: bool
        """
        try:
            async with await self.client.get_client() as s3:
                await s3.head_bucket(Bucket=self.bucket)
            # logger.info(f"Bucker '{self.bucket}' existed.")
            return True
        except Exception as e:
            logger.warning(f"Bucket '{self.bucket}' not found: {str(e)}")
            return False
        
    async def create_bucket(self):
        """
        Check if a bicket exists in MinIO.

        :return: True if the bucket exists, False otherwise.
        """
        if await self.exists_bucket():
            return
        try:
            async with await self.client.get_client() as s3:
                await s3.create_bucket(Bucket=self.bucket)
            logger.info(f"Bucket '{self.bucket}' succesfull created.")
        except Exception as e:
            logger.error(f"Error created bucket '{self.bucket}': {e}")
            raise RuntimeError(f"Error created bucket: {str(e)}")
        
minio_handler = MinioHandler(
    bucket=settings.BUCKET_NAME,
    client=s3_client_manager
)