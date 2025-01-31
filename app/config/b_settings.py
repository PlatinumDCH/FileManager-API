from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ConfigDict

class Settings(BaseSettings):
    PG_URL: str = "postgresql+asyncpg://postgres:000000@localhost:5432/contacts"

    MINIO_URL: str = '127.0.0.1:9090'
    MINIO_ACCESS_KEY: str = 'secter'
    MINIO_SECEET_KEY: str = 'secter'
    MINIO_SECURE: bool = True

    SECRET_KEY_JWT:str = '**************************************'   
    ALGORITHM: str = "******"  

    refresh_token: str = "refresh_token"
    access_token: str = "access_token"
    reset_password_token: str = "reset_password_token"
    email_token: str = "email_token"
    
    MAIL_USERNAME:str = 'exemple@gmail.com'
    MAIL_PASSWORD: str = 'secret'
    MAIL_PORT: int = 111
    MAIL_SERVER: str = 'exemple.com'

    RABBITMQ_URL: str = 'amqp://test:test@127.0.0.1:5672/'

    model_config = SettingsConfigDict(
        extra="ignore", 
        env_file=".env", 
        env_file_encoding="utf-8"
    )


settings = Settings()