from sqlalchemy.ext.asyncio import AsyncSession

from services.mail.tasks import send_verification_email, send_password_reset_email
from app.utils.logger import logger
from app.core.config import settings
from app.db.models.user_model import User
from app.db import crud as user_crud
from app.core.security.jwt import jwt_manager


class EmailService:
    
    async def process_email_confirmation(self, user:User, request, session:AsyncSession):
        email_token = await jwt_manager.create_email_token(
            {"sub": user.email}
        )
        await user_crud.update_token(user, email_token, settings.email_token, session)
        send_verification_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=email_token,
        )
    
    async def process_email_change_pass(self, user, request, db):
        re_pass_token = await jwt_manager.create_re_pass_token(
            {"sub": user.email}
        )
        await user_crud.update_token(
            user, re_pass_token, settings.reset_password_token, db
        )

        send_password_reset_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=re_pass_token,
        )

email_manager = EmailService()

