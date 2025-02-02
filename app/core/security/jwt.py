from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from zoneinfo import ZoneInfo
from abc import ABC, abstractmethod

from app.core.config import settings


class ITokenManager(ABC):
    async def create_access_token(self, data, expire_delta):...
    async def create_refresh_token(self, data, expire_delta):...
    async def create_reset_password_token(self, data, expite_delta):...
    async def create_create_email_token(self, data, expite_delta):...
    async def decode_token(self, token, token_type):...

class TokenManager(ITokenManager):
    """
    Manages JWT token creation and decoding.
    Supports access, refresh, reset_password, and confirm_email tokens.
    """

    def __init__(self):
        self.secret_key = settings.SECRET_KEY_JWT
        self.algorithm = settings.ALGORITHM

    async def create_access_token(
            self,
            data: dict, 
            expires_delta: Optional[float] = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=15)

        to_encode.update({"exp": expire, 'scope':settings.access_token})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
  
        return encoded_jwt

    async def create_refresh_token(
            self, 
            data:dict,
            expires_delta:Optional[float] = None
            ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=1)
        
        to_encode.update({"exp": expire, 'scope':settings.access_token})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
  
        return encoded_jwt
    
    async def create_reset_password_token(
            self, 
            data:dict,
            expires_delta:Optional[float] = None
            ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(hours=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(hours=1)
        
        to_encode.update({"exp": expire, 'scope':settings.reset_password_token})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
  
        return encoded_jwt

    async def create_email_token(
            self, 
            data:dict,
            expires_delta:Optional[float] = None
            ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(hours=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(hours=1)
        
        to_encode.update({"exp": expire, 'scope':settings.email_token})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
  
        return encoded_jwt

    async def decode_token(self, token: str, token_type: str) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            scope = payload.get("scope")
            if scope != token_type:
                raise JWTError("Invalid token scope")

            if (email := payload.get("sub")) is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token missing subject (sub)",
                )

            return email

        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
            )

jwt_manager = TokenManager()

