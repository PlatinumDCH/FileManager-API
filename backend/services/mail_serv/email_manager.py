from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.mail_serv.tasks import (
    send_verification_email,
    send_password_reset_email,
)
from backend.app.utils.logger import logger
from backend.app.core.config import settings
from backend.app.db.models.user_model import User
from backend.app.repository.manager import crud
from backend.app.core.security.secure_token import token_manager, TokenType


class EmailService:

    async def process_email_confirmation(
        self, user: User, request, session: AsyncSession
    ):
        email_token = await token_manager.create_token(
            token_type=TokenType.EMAIL, data={"sub": user.email}
        )
        await crud.tokens.update_token(
            user=user, token=email_token, token_type=TokenType.EMAIL, db=session
        )

        send_verification_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=email_token,
        )

    async def process_email_change_pass(self, user, request, db):
        re_pass_token = await token_manager.create_token(
            token_type=TokenType.RESET_PASSWORD, data={"sub": user.email}
        )
        await crud.tokens.update_token(
            user=user, token=re_pass_token, token_type=TokenType.RESET_PASSWORD, db=db
        )

        send_password_reset_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=re_pass_token,
        )


email_manager = EmailService()
