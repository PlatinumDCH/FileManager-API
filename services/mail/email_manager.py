from sqlalchemy.ext.asyncio import AsyncSession

from services.mail.tasks import send_verification_email, send_password_reset_email
from app.utils.logger import logger
from app.core.config import settings
from app.db.models.user_model import User
from app.db.crud import user_repository
from app.core.security.jwt import token_manager, TokenType


class EmailService:
    
    async def process_email_confirmation(self, user:User, request, session:AsyncSession):
        email_token = await token_manager.create_token(
            token_type=TokenType.EMAIL,
            data={"sub": user.email}
        )
        await user_repository.update_token(
            user=user, 
            token=email_token, 
            token_type=TokenType.EMAIL,
            db=session)
        
        send_verification_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=email_token,
        )
    
    async def process_email_change_pass(self, user, request, db):
        re_pass_token = await token_manager.create_token(
            token_type=TokenType.RESET_PASSWORD,
            data={"sub": user.email}
        )
        await user_repository.update_token(
            user=user, 
            token=re_pass_token, 
            token_type=TokenType.RESET_PASSWORD,
            db=db
        )

        send_password_reset_email.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=re_pass_token,
        )

email_manager = EmailService()

