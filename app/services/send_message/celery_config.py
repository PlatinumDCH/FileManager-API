from celery import Celery
from app.config.b_settings import settings


celery_app = Celery(
    "tasks",
    broker=settings.RABBITMQ_URL, 
    backend="rpc://",
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)