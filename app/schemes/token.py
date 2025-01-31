from pydantic import BaseModel
from enum import Enum

class TokenType(str, Enum):
    RESET_PASSWORD_TOKEN = "reset_password_token"
    EMAIL_TOKEN = "email_token"
    REFRESH_TOKEN = "refresh_token"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenUpdateRequest(BaseModel):
    token: str
    token_type: TokenType  