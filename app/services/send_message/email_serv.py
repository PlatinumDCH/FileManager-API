from app.services.send_message.taks import send_email_task

from app.config.logger import logger
from app.config.b_settings import settings

from app.repository import user as repo_users
from app.utils import jwt_process



class EmailService:
    
    async def process_email_confirmation(self, user, request, db):
        email_token = await jwt_process.EmailTokenService().create_email_token(
            {"sub": user.email}
        )
        await repo_users.update_token(user, email_token, settings.email_token, db)
        send_email_task.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=email_token,
            message_type="confirm_email",
        )
    
    async def process_email_change_pass(self, user, request, db):
        re_pass_token = await jwt_process.ResetPasswordService().create_re_pass_token(
            {"sub": user.email}
        )
        await repo_users.update_token(
            user, re_pass_token, settings.reset_password_token, db
        )

        send_email_task.delay(
            email=user.email,
            username=user.user_name,
            host=str(request.base_url),
            token=re_pass_token,
            message_type="reset_password",
        )

email_service = EmailService()

