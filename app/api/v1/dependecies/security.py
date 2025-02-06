from jose import JWTError
from functools import wraps
from fastapi import Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from app.utils.logger import logger
from app.api.v1.dependecies.client_db import get_conn_db
from app.core.security.jwt import token_manager, TokenType
from app.db.crud import user_repository


class AuthService:
    auth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    async def get_current_user(
        self,
        token: str = Depends(auth2scheme),
        db: AsyncSession = Depends(get_conn_db),
    ):

        credential_exeptions = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            pyload = await token_manager.decode_token(
                token_type=TokenType.ACCESS,
                token=token)
            if (user_email := pyload.get('sub')) is None:
                raise credential_exeptions
            
        except JWTError:
            raise credential_exeptions

        user = await user_repository.get_user_by_email(
            email=user_email, 
            session=db)
        return user
    
    async def get_current_user_role(
            self,
            token: str = Depends(auth2scheme),
            session: AsyncSession = Depends(get_conn_db) 
    ):
        credential_exeptions = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            pyload = await token_manager.decode_token(
                token_type=TokenType.ACCESS,
                token=token
                )
            if (user_email := pyload.get('sub')) is None:
                raise credential_exeptions
            user = await user_repository.get_user_by_email(
                email=user_email, 
                session=session
                )
            logger.info(f"Decoded user role: {user.role}") 
            return user.role
        
        except JWTError:
            raise credential_exeptions
    
def role_required(*allowed_roles: str):
    async def verify_role(role: str = Depends(AuthService().get_current_user_role)):
        # Приводим роль к нижнему регистру для нечувствительного сравнения
        if role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="access banned"
            )
    return Depends(verify_role)



