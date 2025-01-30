from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status

from jose import JWTError, jwt
import pytz

from app.config.b_settings import settings

from abc import ABC, abstractmethod


class ConstructionJWTService(ABC):

    @abstractmethod
    async def create_access_token(
        self, data: dict, expire_delta: Optional[float]
    ) -> str: ...

    @abstractmethod
    async def create_refresh_token(
        self, data: dict, expire_delta: Optional[float]
    ) -> str: ...

    @abstractmethod
    async def decode_token(self, token: str, token_type: str) -> str | None: ...


class JWTService(ConstructionJWTService):
    """working with token, create and decode"""

    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        to_encode = data.copy()
        unc_now = datetime.now(pytz.UTC)

        if expires_delta:
            expire = unc_now + timedelta(minutes=expires_delta)
        else:
            expire = unc_now + timedelta(minutes=45)

        to_encode.update(
            {
                "iat": datetime.now(pytz.UTC),  # time created token
                "exp": expire,  # finishing time token
                "scope": "access_token",  # token type
            }
        )
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        to_encode = data.copy()
        utc_now = datetime.now(pytz.UTC)
        if expires_delta:
            expire = utc_now + timedelta(seconds=expires_delta)
        else:
            expire = utc_now + timedelta(days=7)
        to_encode.update(
            {
                "iat": datetime.now(pytz.UTC),  # time creates token
                "exp": expire,  # finisfing time token
                "scope": "refresh_token",  # type token
            }
        )
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def decode_token(self, token: str, token_type: str) -> str:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            exp = payload.get("exp")
            if exp is None:
                raise JWTError("Token has no expiration time")

            utc_now = datetime.now(pytz.UTC)
            if utc_now > datetime.fromtimestamp(exp, tz=pytz.UTC):
                raise JWTError("Break time action token")

            scope = payload.get("scope")
            if scope != token_type:
                raise JWTError("Invalid token scope")

            email = payload.get("sub")
            if email is None:
                raise JWTError("Token missing  subject (sub)")

            return email

        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
            )
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
            )


jwt_serv = JWTService()
