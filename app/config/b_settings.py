from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict

class Settings(BaseSettings):
    PG_URL: str = "postgresql+asyncpg://postgres:000000@localhost:5432/contacts"

    MINIO_URL: str = '127.0.0.1:9090'
    MINIO_ACCESS_KEY: str = 'secter'
    MINIO_SECEET_KEY: str = 'secter'
    MINIO_SECURE: bool = True

    model_config = SettingsConfigDict(
        extra="ignore", 
        env_file=".env", 
        env_file_encoding="utf-8"
    )


settings = Settings()