from pydantic import BaseModel, EmailStr, Field

class ResetPasswordSchema(BaseModel):
    email:EmailStr

class ResetForgerPassword(BaseModel):
    secret_token: str
    new_password: str
    confirm_password: str

class SuccesMessage(BaseModel):
    success: bool
    status_code: int
    message: str