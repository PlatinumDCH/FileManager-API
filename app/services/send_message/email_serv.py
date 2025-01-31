from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.config.logger import logger
from app.services.send_message.producer import send_to_rabbit
from app.config.b_settings import settings
from app.schemes.user import ShowUser
from app.repository import user as repo_users
from app.utils import jwt_process
from app.models.user_model import User


class EmailService:

    async def send_email(self, email_task: dict):
        """
        send email rask on rabbitmq
        exemple =   {'email':new_user.email,
                     'username':new_user.username,
                     'host': str(request.base_url),
                     'queue_name':'confirm_email',
                     'token': < email_token >}
        """
        try:
            await send_to_rabbit(email_task)
        except Exception as err:

            raise

    async def pocess_email_confirmation(
        self, user: User, request: Request, db: AsyncSession
    ):

        email_token = await jwt_process.EmailTokenService().create_email_token(
            {"sub": user.email}
        )
        await repo_users.update_token(user, email_token, settings.email_token, db)
        email_task = {
            "email": user.email,
            "username": user.user_name,
            "host": str(request.base_url),
            "queue_name": "confirm_email",
            "token": settings.email_token,
        }
        await self.send_email(email_task)

    async def process_email_change_pass(
        self, user: User, request: Request, db: AsyncSession
    ):
        re_pass_token = await jwt_process.ResetPasswordService().create_re_pass_token(
            {"sub": user.email}
        )
        await repo_users.update_token(
            user, re_pass_token, settings.reset_password_token, db
        )

        email_task = {
            "email": user.email,
            "username": user.user_name,
            "host": str(request.base_url),
            "queue_name": "reset_password",
            "token": settings.reset_password_token,
        }
        await self.send_email(email_task)


email_service = EmailService()
