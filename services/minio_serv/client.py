import aioboto3  # type: ignore
from app.core.config import settings
from abc import ABC, abstractmethod

class IClient(ABC):
    @abstractmethod
    async def get_client(self):
        pass

class S3ClientManager(IClient):
    """
    A class to manage the creation and configuration of the S3 clien.
    """
    def __init__(
            self,  
            access_key: str, 
            secret_key: str, 
            endpoint: str, 
            secure : bool = True
    ):
        """
        Initialize the MinIOHandler with the necessart credentioal ans configuration.
        
        :param bucket: The name of the bucket to interact with.
        :param access_key: The access key for MinIO.
        :param secret_key: The secret key for MinIO.
        :param endpoint: The endpoint URL for MinIO.
        :param secure:Where to user HTTPS (True) or HTTP (False).
        """
        self.session = aioboto3.Session()
        self.endpoint_url = f"{'https' if secure else 'http'}://{endpoint}"
        self.credentials = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key
        }
    
    async def get_client(self):
        """
        Create and return an S3 client.
        
        :return: An S3 client instance.
        """
        return self.session.client(
            "s3", 
            endpoint_url=self.endpoint_url,
            **self.credentials)

s3_client_manager = S3ClientManager(
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECEET_KEY,
    endpoint=settings.MINIO_URL,
    secure=settings.MINIO_SECURE,
)