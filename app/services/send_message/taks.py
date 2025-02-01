from pydantic import SecretStr
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.config.b_settings import settings
import asyncio
from app.services.send_message.celery_config import celery_app
from app.config.b_settings import settings


BASE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

# Конфигурация почты
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Contact server",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=BASE_DIR,
)

def create_message_schema(email, host, username, token, message_type):
    if message_type == "reset_password":
        subject = "Changer server-pas"
        template_name = "password_reset/password_reset.html"
    elif message_type == "confirm_email":
        subject = "Changer server-email"
        template_name = "email_confirm/email_confirm.html"
    else:
        raise ValueError(f"Unknown message type: {message_type}")

    template_data = {
        "host": host,
        "username": username,
        "token": token,
    }

    return MessageSchema(
        subject=subject,
        recipients=[email],
        template_body=template_data,
        subtype=MessageType.html,
    ), template_name

async def _send_email(email, host, username, token, message_type):
    """anync f for send mail."""
    try:
        message_schema, template_name = create_message_schema(
            email, host, username, token, message_type
        )
        fm = FastMail(conf)
        await fm.send_message(message_schema, template_name=template_name)
      
    except Exception as e:
        raise

@celery_app.task(bind=True, max_retries=3)
def send_email_task(self, email, host, username, token, message_type):
    """task Celery from send mail."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_send_email(email, host, username, token, message_type))
    except Exception as e:
        raise self.retry(exc=e)