from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User
from app.utils.security import auth_serv
from app.utils.jwt_process import jwt_serv
from app.config.client_db import get_conn_db
from app.repository import user as repo_user
from app.utils.pass_serv import Hasher
from app.config.client_db import get_conn_db
from app.schemes.user import ShowUser, UserCreate
from app.schemes.token import Token

router = APIRouter()


@router.post("/signup", response_model=ShowUser, status_code=status.HTTP_201_CREATED)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_conn_db)):

    if await repo_user.exist_user(body.email, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="accaunt already exists"
        )

    body.password_plain = Hasher.get_password_hesh(body.password_plain)
    new_user = await repo_user.create_new_user(body, db)

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
    encode_access_token = await jwt_serv.create_access_token(
        data={"sub": user.email}
    )
    encode_refresh_token = await jwt_serv.create_refresh_token(
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
