from jose import JWTError
from fastapi import Depends, Request, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.utils.logger import logger
from backend.app.api.dependecies.client_db import get_conn_db
from backend.app.core.security.secure_token import token_manager, TokenType
from backend.app.db.crud import user_repository



class AuthService:
    async def get_current_user(
            self,
            request: Request,
            db:AsyncSession = Depends(get_conn_db)
    ):
        credential_exeptions = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = request.cookies.get('access_token')

        if token is None:
            raise credential_exeptions

        try:
            pyload = await token_manager.decode_token(
                token_type=TokenType.ACCESS,
                token=token
            )
            if (user_email := pyload.get('sub')) is None:
                raise credential_exeptions
        except JWTError:
            raise credential_exeptions
        
        user = await user_repository.get_user_by_email(
            email=user_email,
            session=db
        )

        if user is None:
            raise credential_exeptions
        
        return user
    
    async def get_current_user_role(
            self,
            request:Request,
            session: AsyncSession = Depends(get_conn_db) 
    ):
        credential_exeptions = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            token = request.cookies.get('access_token')

            if token is None:
                raise credential_exeptions
            
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
        if role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="access banned"
            )
    return Depends(verify_role)
