from pydantic import SecretStr
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType



import asyncio

from services.email_sender import render_template, send_email
from services.config.celery_app import app


@app.task(queue='email_verification', bind=True, max_retries=3)
def send_verification_email(self, email, username, host, token):
    """Отправка письма для подтверждения email."""
    try:
        html_content = render_template(
            'verification_email.html',
            username=username,
            host=host,
            token=token
        )
        send_email(email, "Verify Your Email", html_content)
    except Exception as e:
        self.retry(exc=e, countdown=60)

@app.task(queue='password_reset', bind=True, max_retries=3)
def send_password_reset_email(self, email, username, host, token):
    """Отправка письма для сброса пароля."""
    try:
        html_content = render_template(
            'reset_password.html',
            username=username,
            host=host,
            token=token
        )
        send_email(email, "Password Reset Request", html_content)
    except Exception as e:
        self.retry(exc=e, countdown=60)
