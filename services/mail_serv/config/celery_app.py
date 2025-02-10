from celery import Celery
from app.core.config import settings


app = Celery(
    "tasks",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
)

app.conf.task_queues = {
    "email_verification": {"exchange": "email_verification"},
    "password_reset": {"exchange": "password_reset"},
}
