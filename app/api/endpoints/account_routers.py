from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import FileResponse
from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from services.mail_serv.email_manager import email_manager
from app.core.security.security_password import Hasher
from app.db.crud import user_repository
from app.api.dependecies.client_db import get_conn_db
from app.core.security.jwt import token_manager, TokenType
from app.db import schemas as shs
from app.core.config import settings


router = APIRouter(prefix="/account")


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    body: shs.RequestForgotPassword, 
    request:Request,
    session: AsyncSession = Depends(get_conn_db)
):
    """
    send email link to page forgot password

    get userEmail by email /email-None
    verify email
    create token resetPsword
    send email to emailService
    """

    curent_user = await user_repository.get_user_by_email(body.email, session)
    if not curent_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    await email_manager.process_email_change_pass(curent_user, request, session)
    return {"message": "Check you email for reset password"}


@router.post("/reset-password", response_model=shs.SuccesMessage)
async def reset_password(
    body: shs.ResetForgotPassword, session: AsyncSession = Depends(get_conn_db)
):
    """
    reset password endpoint
    :param rfp: pydantic{secret_token:str, new_password:str, confirm_password:str}
    :param session:

    :descriptions:  1.decode token, get user_email
                    2.get UserObject, by user_email
                    3.ferify new passrod
                    4.heshed new password
                    5.save new hashed password to UserObject
    """
    try:
        pyload = await token_manager.decode_token(
            token_type=TokenType.RESET_PASSWORD,
            token = body.reset_password_token
        )
        if (user_email := pyload.get('sub')) is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Password Reset Payload or Reset Link Expired",
            )
        if body.new_password != body.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="New password and confirm password are not same.",
            )
        user = await user_repository.get_user_by_email(user_email, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification error, user not found",
            )
        identic_password = Hasher.verify_password(
            plain_password=body.new_password, 
            hashed_password=user.password)
        if identic_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password is the same as old password",
            )
        hashed_password = Hasher.get_password_hash(
            password=body.new_password
            )
        await user_repository.update_user_password(
            user=user, 
            hashed_password=hashed_password, 
            session=session)

        await user_repository.update_token(
            user=user, 
            token=None,
            token_type=TokenType.RESET_PASSWORD,
            db=session)
        return {
            "success": True,
            "status_code": status.HTTP_200_OK,
            "message": "Password Rest Successfull!",
        }
    except HTTPException as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Some thing unexpected happened",
        )


@router.post("/resend-confirmation-email", status_code=status.HTTP_200_OK)
async def resend_confirmation_email(
    body: shs.ResendEmail,
    request: Request,
    session: AsyncSession = Depends(get_conn_db),
):
    """
    email confirm, repeat send email
    :param bode: pydantic({email:EmailStr})
    :param request:
    :param session:
    :returns : message status send email
    :raises: emeil yield confirm
    """
    curent_user = await user_repository.get_user_by_email(
        email=body.email, 
        session=session)
    if not curent_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if curent_user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email is already confirmed",
        )
    
    await email_manager.process_email_confirmation(curent_user,request,session)                              
    
    return {"message": "Email send, check you post for confirmation"}

@router.post("/confirm-email", status_code=status.HTTP_200_OK)
async def confirm_email(
    body: shs.RequestConfirmEmail, session: AsyncSession = Depends(get_conn_db)
):
    """
    process confirmed email user emailToken.

    This endpoint check EmailToken, updata user.confirmed column, del old token
    :params token:
    :patams db: session
    :returns: message, sucesful & Exception (user not found)

    """
    pyload = await token_manager.decode_token(
        token_type=TokenType.RESET_PASSWORD,
        token = body.email_token
        )
    if (user_email := pyload.get('sub')) is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Password Reset Payload or Reset Link Expired",
            )
    curent_user = await user_repository.get_user_by_email(user_email, session)
    if curent_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error, user not found",
        )
    if curent_user.confirmed:
        return {"message": "Your email already confirmed"}

    await user_repository.confirmed_email(user=curent_user, session=session, value=True)
    await user_repository.update_token(
        curent_user, 
        None, 
        TokenType.EMAIL, 
        session)
    return {"message": "Email confirmed"}

@router.get("/track-email-open/{username}")
async def request_email(
    username: str, response: Response):
    """
    endpoint for tracking the opening of a letter by the recipient
    :param username: nameUser, connected with request
    :param response:
    :db: async session
    :returns: shadow pixel

    """
    print(f"{username} open email")
    return FileResponse(
        "services/mail/templates/static/open_check.png",
        media_type="image/png",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
        content_disposition_type="inline",
    )


