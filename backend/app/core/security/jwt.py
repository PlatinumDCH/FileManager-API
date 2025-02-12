from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from zoneinfo import ZoneInfo
from abc import ABC, abstractmethod
from enum import Enum
from typing import Type
from backend.app.core.config import settings

class TokenType(str, Enum):
    ACCESS = 'access_token'
    REFRESH = 'refresh_token'
    RESET_PASSWORD = 'reset_password_token'
    EMAIL = 'email_token'


#abstract strategy
class ITokenStrategy(ABC):
    @abstractmethod
    async def create_token(self, data, expire_delta:Optional[float]= None):
        pass
    
    @abstractmethod
    async def decode_token(self, token)->dict: 
        pass

class AccessTokenStrategy(ITokenStrategy):
    def __init__(self):
        self.secret_key = settings.SECRET_KEY_JWT
        self.algorithm = settings.ALGORITHM
    
    async def create_token(
            self, 
            data: dict, 
            expires_delta: Optional[float] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=60)
        to_encode.update({"exp": expire, "scope": TokenType.ACCESS})
        return jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("scope") != TokenType.ACCESS:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token scope")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token")

class RefreshTokenStrategy(ITokenStrategy):
    def __init__(self):
        self.secret_key = settings.SECRET_KEY_JWT
        self.algorithm = settings.ALGORITHM
    
    async def create_token(
            self, data: dict, 
            expires_delta: Optional[float] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=1)

        to_encode.update({"exp": expire, "scope": TokenType.REFRESH})
        return jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("scope") != TokenType.REFRESH:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token scope")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token")
    
class ResetPasswordTokenStrategy(ITokenStrategy):
    def __init__(self):
        self.secret_key = settings.SECRET_KEY_JWT
        self.algorithm = settings.ALGORITHM
    
    async def create_token(
            self, 
            data: dict, 
            expires_delta: Optional[float] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=30)
        to_encode.update({"exp": expire, "scope": TokenType.RESET_PASSWORD})
        return jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("scope") != TokenType.RESET_PASSWORD:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token scope")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token")

class EmailTokenStrategy(ITokenStrategy):
    def __init__(self):
        self.secret_key = settings.SECRET_KEY_JWT
        self.algorithm = settings.ALGORITHM
    
    async def create_token(
            self, 
            data: dict, 
            expires_delta: Optional[float] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(ZoneInfo('UTC')) + timedelta(minutes=30)
        to_encode.update({"exp": expire, "scope": TokenType.EMAIL})
        return jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm)

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("scope") != TokenType.EMAIL:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token scope")
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid token")

#fabrik strategy
class TokenStrategyFactory:
    _strategies : dict[TokenType, Type[ITokenStrategy]] = {
        TokenType.ACCESS: AccessTokenStrategy,
        TokenType.REFRESH: RefreshTokenStrategy,
        TokenType.RESET_PASSWORD: ResetPasswordTokenStrategy,
        TokenType.EMAIL: EmailTokenStrategy,
    }

    @classmethod
    def get_strategy(cls, token_type:TokenType) -> ITokenStrategy:
        strategy_class = cls._strategies.get(token_type)
        if not strategy_class:
            raise ValueError(f'unsupported token type: {token_type}')
        return strategy_class()

class TokenManager:
    def __init__(self):
        self.strategy_factory = TokenStrategyFactory()

    async def create_token(self, token_type:TokenType, data: dict, expire_delta: Optional[float] = None) -> str:
        strategy = self.strategy_factory.get_strategy(token_type)
        return await strategy.create_token(data, expire_delta)
    
    async def decode_token(self, token_type:TokenType,  token: str) -> dict:
        strategy = self.strategy_factory.get_strategy(token_type)
        return await strategy.decode_token(token)


token_manager = TokenManager()
