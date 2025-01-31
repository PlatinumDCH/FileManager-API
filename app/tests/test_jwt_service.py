import pytest
import asyncio
from datetime import timedelta
from jose import jwt

from app.services.jwt_process import (
    AccessTokenService,
    RefreshTokenService,
    EmailTokenService,
    ResetPasseordService,
    BaseWJTService
)
from app.config.b_settings import settings


@pytest.fixture
def test_data():
    return {"sub": "test@example.com"}

@pytest.mark.asyncio
async def test_create_access_token(test_data):
    service = AccessTokenService()
    token = await service.create_access_token(test_data, expires_delta=10)  # 10 minutes

    assert isinstance(token, str)

    decoded = await service.decode_token(token, settings.access_token)
    assert decoded == "test@example.com"

@pytest.mark.asyncio
async def test_create_refresh_token(test_data):
    service = RefreshTokenService()
    token = await service.create_refresh_token(test_data, expires_delta=1)  # 1 day

    assert isinstance(token, str)

    decoded = await service.decode_token(token, settings.refresh_token)
    assert decoded == "test@example.com"

@pytest.mark.asyncio
async def test_create_email_token(test_data):
    service = EmailTokenService()
    token = await service.create_email_token(test_data, expires_delta=1)  # 1 hour

    assert isinstance(token, str)

    decoded = await service.decode_token(token, settings.email_token)
    assert decoded == "test@example.com"

@pytest.mark.asyncio
async def test_create_reset_password_token(test_data):
    service = ResetPasseordService()
    token = await service.create_re_pass_token(test_data, expires_delta=1)  # 1 hour

    assert isinstance(token, str)

    decoded = await service.decode_token(token, settings.reset_password_token)
    assert decoded == "test@example.com"

@pytest.mark.asyncio
async def test_expired_token(test_data):
    service = AccessTokenService()
    
    expired_token = jwt.encode(
        {"sub": "test@example.com", "exp": 0},  # exp = 0 → broken token
        settings.SECRET_KEY_JWT,
        algorithm=settings.ALGORITHM
    )

    with pytest.raises(Exception) as exc_info:
        await service.decode_token(expired_token, settings.access_token)
    
    assert 'Signature has expired' in str(exc_info.value)

@pytest.mark.asyncio
async def test_invalid_token():
    service = AccessTokenService()
    
    fake_token = "invalid.token.here"

    with pytest.raises(Exception) as exc_info:
        await service.decode_token(fake_token, settings.access_token)
    
    assert 'Invalid token format' in str(exc_info.value)

@pytest.mark.asyncio
async def test_wrong_scope(test_data):
    service = AccessTokenService()
    token = await service.create_access_token(test_data)

    with pytest.raises(Exception) as exc_info:
        await service.decode_token(token, settings.refresh_token)  # error: input refresh & access
    
    assert "Invalid token scope" in str(exc_info.value)
