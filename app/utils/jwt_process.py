from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
import pytz

from app.config.b_settings import settings

from abc import ABC, abstractmethod


class IBaseJWTService(ABC):

    @abstractmethod
    async def create_token(
        self, data: dict, expire_delta: Optional[float], token_type, time_unit
    ) -> str: ...

    @abstractmethod
    async def decode_token(self, token: str, token_type: str) -> str | None: ...


class BaseWJTService(IBaseJWTService):
    SECRET_KEY = settings.SECRET_KEY_JWT
    ALGORITHM = settings.ALGORITHM
    DEFAULT_EXPIRATION = 45  # minutes

    async def create_token(
        self,
        data: dict,
        expires_delta: Optional[float],
        token_type: str,
        time_unit: str = "minutes",
    ):
        """
        generation jwtToken universal
        :param data: data for encode
        :param expire_delta: time live token
        :param toke_type: type token
        :param time_unit: timeValue(minutes, hours, days, seconds)
        :return jwtToken
        """
        to_encode = data.copy()
        utc_now = datetime.now(pytz.UTC)

        time_units = {
            "seconds": timedelta(seconds=expires_delta or 3600),
            "minutes": timedelta(minutes=expires_delta or self.DEFAULT_EXPIRATION),
            "hours": timedelta(hours=expires_delta or 12),
            "days": timedelta(days=expires_delta or 7),
        }

        expire = utc_now + time_units.get(
            time_unit, timedelta(minutes=self.DEFAULT_EXPIRATION)
        )

        to_encode.update(
            {
                "iat": utc_now,
                "exp": expire,
                "scope": token_type,
            }
        )
        return jwt.encode(to_encode, self.SECRET_KEY, self.ALGORITHM)

    async def decode_token(self, token: str, token_type: str) -> str:
        """check token & return user email"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if (exp := payload.get("exp")) is None:
                raise JWTError("Token has no expiration time")

            utc_now = datetime.now(pytz.UTC)
            if utc_now > datetime.fromtimestamp(exp, tz=pytz.UTC):
                raise JWTError("Break time action token")

            scope = payload.get("scope")
            if scope != token_type:
                raise JWTError("Invalid token scope")

            if (email := payload.get("sub")) is None:
                raise JWTError("Token missing  subject (sub)")

            return email

        except JWTError as err:
            if "Invalid header string" in str(err):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token format",
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
            )


class AccessTokenService(BaseWJTService):
    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None,
        token_type: str = settings.access_token,
    ) -> str:
        return await self.create_token(
            data, expires_delta, token_type=token_type, time_unit="minutes"
        )


class RefreshTokenService(BaseWJTService):
    async def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None,
        token_type: str = settings.refresh_token,
    ) -> str:
        return await self.create_token(
            data, expires_delta, token_type=token_type, time_unit="days"
        )


class EmailTokenService(BaseWJTService):
    async def create_email_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None,
        token_type: str = settings.email_token,
    ) -> str:
        return await self.create_token(
            data, expires_delta, token_type=token_type, time_unit="hours"
        )


class ResetPasswordService(BaseWJTService):
    async def create_re_pass_token(
        self,
        data: dict,
        expires_delta: Optional[float] = None,
        token_type: str = settings.reset_password_token,
    ) -> str:
        return await self.create_token(
            data, expires_delta, token_type=token_type, time_unit="hours"
        )
