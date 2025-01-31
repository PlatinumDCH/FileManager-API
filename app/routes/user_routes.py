from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemes.reset_password import ResetPasswordSchema
from app.config.logger import logger
from app.models.user_model import User
from app.dependencies.security import auth_serv
from app.utils import jwt_process
from app.config.client_db import get_conn_db
from app.repository import user as repo_user
from app.utils.pass_serv import Hasher
from app.config.client_db import get_conn_db
from app.schemes.user import ShowUser, UserCreate
from app.schemes.token import Token
from app.services.send_message import email_serv as email_process

router = APIRouter()


@router.post("/signup", response_model=ShowUser, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, request:Request, db: AsyncSession = Depends(get_conn_db)):

    if await repo_user.exist_user(body.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="accaunt already exists"
        )

    body.password_plain = Hasher.get_password_hesh(body.password_plain)
    new_user = await repo_user.create_new_user(body, db)
    logger.info(f'Create user {new_user.email}${new_user.user_name}')
    await email_process.email_service.pocess_email_confirmation(new_user, request, db)
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  
    db: AsyncSession= Depends(get_conn_db)):
    user = await repo_user.autenticate_user(form_data.username, form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Account not confirmed, check email'
        )
    
    encode_access_token = await jwt_process.AccessTokenService().create_access_token(
        data={"sub": user.email}
    )
    encode_refresh_token = await jwt_process.RefreshTokenService().create_refresh_token(
        data={'sub': user.email}
    )

    return {
        "access_token": encode_access_token, 
        "refresh_token": encode_refresh_token,
        "token_type": "bearer"}

@router.get('/me')
async def get_me(user:User = Depends(auth_serv.get_current_user)):
    return {
        'message':'corectly work'
    }

@router.post('/reset_password_request')
async def forgot_password(
    body:ResetPasswordSchema,
    request:Request,
    db:AsyncSession=Depends(get_conn_db)
):
    """
    send mail link to page forgot password

    get userEmail by email /email-None
    verify email
    create token resetPsword
    send email to emailService
    """
    curent_user = await repo_user.get_user_by_email(body.email, db)
    if not curent_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )

    await email_process.email_service.process_email_change_pass(
        curent_user,
        request,
        db
    )
    return {
        'message':'Check you email for reset password'
    }