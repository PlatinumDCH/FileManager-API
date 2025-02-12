import pytest
from fastapi import HTTPException, status
from backend.app.core.security.jwt import  TokenType, ITokenStrategy, TokenStrategyFactory, TokenManager

@pytest.fixture
def token_manager():
    return TokenManager()


@pytest.mark.asyncio
async def test_create_and_decode_access_token(token_manager):
    data = {"user_id": 1}
    token = await token_manager.create_token(TokenType.ACCESS, data, expire_delta=60)
    decoded = await token_manager.decode_token(TokenType.ACCESS, token)
    assert decoded["user_id"] == 1
    assert decoded["scope"] == TokenType.ACCESS

@pytest.mark.asyncio
async def test_create_and_decode_refresh_token(token_manager):
    data = {"user_id": 1}
    token = await token_manager.create_token(TokenType.REFRESH, data, expire_delta=1)
    decoded = await token_manager.decode_token(TokenType.REFRESH, token)
    assert decoded["user_id"] == 1
    assert decoded["scope"] == TokenType.REFRESH

@pytest.mark.asyncio
async def test_create_and_decode_reset_password_token(token_manager):
    data = {"user_id": 1}
    token = await token_manager.create_token(TokenType.RESET_PASSWORD, data, expire_delta=30)
    decoded = await token_manager.decode_token(TokenType.RESET_PASSWORD, token)
    assert decoded["user_id"] == 1
    assert decoded["scope"] == TokenType.RESET_PASSWORD

@pytest.mark.asyncio
async def test_create_and_decode_email_token(token_manager):
    data = {"user_id": 1}
    token = await token_manager.create_token(TokenType.EMAIL, data, expire_delta=30)
    decoded = await token_manager.decode_token(TokenType.EMAIL, token)
    assert decoded["user_id"] == 1
    assert decoded["scope"] == TokenType.EMAIL

# Тесты для обработки ошибок
@pytest.mark.asyncio
async def test_decode_invalid_token(token_manager):
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        await token_manager.decode_token(TokenType.ACCESS, invalid_token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token"

@pytest.mark.asyncio
async def test_decode_token_with_wrong_scope(token_manager):
    data = {"user_id": 1}
    token = await token_manager.create_token(TokenType.ACCESS, data, expire_delta=60)
    with pytest.raises(HTTPException) as exc_info:
        await token_manager.decode_token(TokenType.REFRESH, token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc_info.value.detail == "Invalid token scope"

@pytest.mark.asyncio
async def test_unsupported_token_type(token_manager):
    with pytest.raises(ValueError) as exc_info:
        await token_manager.create_token("unsupported_type", {"user_id": 1})
    assert "unsupported token type" in str(exc_info.value)

# Тесты для TokenStrategyFactory
def test_token_strategy_factory():
    strategy = TokenStrategyFactory.get_strategy(TokenType.ACCESS)
    assert isinstance(strategy, ITokenStrategy)

    strategy = TokenStrategyFactory.get_strategy(TokenType.REFRESH)
    assert isinstance(strategy, ITokenStrategy)

    strategy = TokenStrategyFactory.get_strategy(TokenType.RESET_PASSWORD)
    assert isinstance(strategy, ITokenStrategy)

    with pytest.raises(ValueError):
        TokenStrategyFactory.get_strategy("unsupported_type")

@pytest.mark.asyncio
async def test_get_email_token(token_manager):
    data = {'sub':'exemple@gmail.com'}
    token = await token_manager.create_token(TokenType.ACCESS, data, expire_delta=60)
    decoded = await token_manager.decode_token(TokenType.ACCESS, token)

    assert decoded.get('sub') == 'exemple@gmail.com'