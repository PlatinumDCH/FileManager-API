from fastapi.security import OAuth2PasswordRequestForm

from fastapi import APIRouter, Request, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependecies.client_db import get_conn_db

from app.core.security.jwt import token_manager, TokenType

from app.core.security.security_password import Hasher
from app.api.dependecies.security import AuthService
from app.db.crud import user_repository
from app.db import schemas as shs
from app.utils.logger import logger
from services.mail_serv.email_manager import email_manager

router = APIRouter(prefix="/auth")



@router.post("/register", response_model=shs.ResponseUser, status_code=200)
async def register_user(
    body: shs.RegisterUser,
    request : Request,
    session: AsyncSession = Depends(get_conn_db),
):
    if await user_repository.exist_user(body.email, session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="accaunt already exists"
        )

    body.password = Hasher.get_password_hash(body.password)
    new_user = await user_repository.create_new_user(body, session)

    logger.info(f"Register new user {body.user_name}--{body.email}")

    #logic send email
    await email_manager.process_email_confirmation(new_user,request,session)
    return shs.ResponseUser.model_validate(new_user)


@router.post("/login", response_model=shs.ResponseAutorization)
async def autorization(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    :param form_data: fd.username, fd.password
    :session :

    autenticate user by email,password
    createAccessToken
    createRefreshToken
    save refreshToken to database
    return ResponseAutorization
    """
    user = await user_repository.autenticate_user(
        email=form_data.username, password=form_data.password, session=session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You banned'
        )
    
    # validation confirmed user email adress
    encode_access_token = await token_manager.create_token(
        TokenType.ACCESS,
        data={"sub": user.email})
    encode_refresh_token = await token_manager.create_token(
        TokenType.REFRESH,
        data={"sub": user.email})
    
    await user_repository.update_token(
        user, 
        encode_refresh_token, 
        TokenType.REFRESH, 
        session
    )
    return shs.ResponseAutorization(access_token=encode_access_token)


@router.post("/logout")
async def logout(
    auth_user=Depends(AuthService().get_current_user),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    clear refresh token in database
    """
    await user_repository.update_token(auth_user, None, TokenType.REFRESH, session)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=shs.ResponseUser)
async def me(
    auth_user=Depends(AuthService().get_current_user),
):
    """
    get info about current user
    headers Autorization: Bearer <token>
    """
    return shs.ResponseUser.model_validate(auth_user)

@router.delete("/me")
async def delete_me(
    auth_user=Depends(AuthService().get_current_user),
    session: AsyncSession = Depends(get_conn_db),
):
    """
    delete user
    headers Autorization: Bearer <token>
    """
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await user_repository.delete_user_from_db(auth_user, session)
    return {"message": "User deleted succesfully"}
