import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from jose import JWTError
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security.jwt import TokenManager


@pytest.fixture
def token_manager():
    return TokenManager()


@pytest.mark.asyncio
async def test_create_access_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_access_token(data, expires_delta=15)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_decode_access_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_access_token(data, expires_delta=15)
    decoded_email = await token_manager.decode_token(token, settings.access_token)
    assert decoded_email == "user@example.com"


@pytest.mark.asyncio
async def test_decode_invalid_scope(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_access_token(data, expires_delta=15)
    with pytest.raises(HTTPException) as exc_info:
        await token_manager.decode_token(token, "invalid_scope")
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid token scope" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_decode_expired_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_access_token(data, expires_delta=-1)  # Токен с истекшим сроком
    with pytest.raises(HTTPException) as exc_info:
        await token_manager.decode_token(token, settings.access_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Signature has expired." in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_decode_missing_sub(token_manager):
    data = {"email": "user@example.com"}  # mising "sub"
    token = await token_manager.create_access_token(data, expires_delta=15)
    with pytest.raises(HTTPException) as exc_info:
        await token_manager.decode_token(token, settings.access_token)
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Token missing subject (sub)" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_refresh_token(token_manager):

    data = {"sub": "user@example.com"}
    token = await token_manager.create_refresh_token(data, expires_delta=1)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_create_reset_password_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_reset_password_token(data, expires_delta=1)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_create_email_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_email_token(data, expires_delta=1)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_decode_refresh_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_refresh_token(data, expires_delta=1)
    decoded_email = await token_manager.decode_token(token, settings.access_token)
    assert decoded_email == "user@example.com"


@pytest.mark.asyncio
async def test_decode_reset_password_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_reset_password_token(data, expires_delta=1)
    decoded_email = await token_manager.decode_token(token, settings.reset_password_token)
    assert decoded_email == "user@example.com"


@pytest.mark.asyncio
async def test_decode_email_token(token_manager):
    data = {"sub": "user@example.com"}
    token = await token_manager.create_email_token(data, expires_delta=1)
    decoded_email = await token_manager.decode_token(token, settings.email_token)
    assert decoded_email == "user@example.com"