from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PG_URL: str = "postgresql+asyncpg://postgres:000000@localhost:5432/contacts"
    database_url_test:str = "sqlite+aiosqlite:///:memory:"

    MINIO_URL: str = '127.0.0.1:9090'
    MINIO_ACCESS_KEY: str = 'secter'
    MINIO_SECEET_KEY: str = 'secter'
    MINIO_SECURE: bool = True
    BUCKET_NAME: str = "test-name"

    SECRET_KEY_JWT:str = '**************************************'   
    ALGORITHM: str = "******"  
 
    MAIL_USERNAME:str = 'exemple@gmail.com'
    MAIL_PASSWORD: str = 'secret'
    MAIL_PORT: int = 111
    MAIL_SERVER: str = 'exemple.com'

    RABBITMQ_URL: str = 'amqp://test:test@127.0.0.1:5672/'

    FileExtensionsPath: Path = Path('backend/app/core/AllowedExtensions.json')
    MAX_SIZE :int  = 5 * 1024 * 1024
    model_config = SettingsConfigDict(
        extra="ignore", 
        env_file=".env", 
        env_file_encoding="utf-8"
    )


settings = Settings()