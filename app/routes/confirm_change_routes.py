from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request

from app.config.logger import logger
from app.utils.pass_serv import Hasher
from app.schemes.user import ResendEmail
from app.schemes.reset_password import SuccesMessage, ResetForgerPassword
from app.services.send_message.email_serv import email_service
import app.repository.user as repo_user
from app.utils import jwt_process
from app.config.b_settings import settings
from app.config.client_db import get_conn_db

router = APIRouter()

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_conn_db)):
    """
    process confirmed email user rmailToken.

    This endpoint check EmailToken, updata user.confirmed column, del old token
    :params token:
    :patams db: session
    :returns: message, sucesful & Exception (user not found)

    """
    email = await jwt_process.BaseWJTService().decode_token(token, settings.email_token)
    user = await repo_user.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error, user not found",
        )
    if user.confirmed:
        return {"message": "Your email already confirmed"}
    # change filed confirmed in UserTable
    await repo_user.confirmed_email(email, db)
    await repo_user.update_token(user, None, settings.email_token, db)
    return {"message": "Email confirmed"}


@router.get("/{username}")
async def request_email(
    username: str, response: Response, db: AsyncSession = Depends(get_conn_db)
):
    """
    endpoint for tracking the opening of a letter by the recipient
    :param username: nameUser, connected with request
    :param response:
    :db: async session
    :returns: shadow pixel

    """
    print(f'{username} open email')
    return FileResponse(
        "app/templates/static/open_check.png",
        media_type="image/png",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        content_disposition_type="inline",
    )


@router.post("/re_email")
async def resend_email_confirm(
    email: ResendEmail, request: Request, db: AsyncSession = Depends(get_conn_db)
):
    """
    email confirm, repeat send email
    :param email:
    :param request:
    :param db: session
    :returns : message status send email
    :raises: emeil yield confirm
    """
    user = await repo_user.get_user_by_email(email, db)
    if user:
        if user.confirmed:
            return {"message": "You email is already confirmed"}
        await email_service.pocess_email_confirmation(user, request, db)
    return {"message": "Email send, check you post for confirmation"}

@router.post('/reset-password', response_model=SuccesMessage)
async def reset_password(
    rfp: ResetForgerPassword,
    db: AsyncSession = Depends(get_conn_db)
):
    try:
        info = await jwt_process.BaseWJTService().decode_token(
            rfp.secret_token,
            settings.reset_password_token
        )
        if info is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Invalid Password Reset Payload or Reset Link Expired")
        if rfp.new_password != rfp.confirm_password:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='new password and confirm password are not same.')
        user = await repo_user.get_user_by_email(info, db)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Verification error, user not found')
        identic_password =  Hasher.verify_password(rfp.new_password, user.hashed_password)
        if identic_password:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='New password is the same as old password')
        hashed_password = Hasher.get_password_hesh(rfp.new_password)
        await repo_user.update_user_password(user, hashed_password, db)
        await repo_user.update_token(user, None, settings.reset_password_token, db)
        return {'success': True, 'status_code': status.HTTP_200_OK,
                 'message': 'Password Rest Successfull!'}
    except HTTPException as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Some thing unexpected happened')