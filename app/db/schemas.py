from pydantic import BaseModel, EmailStr
from datetime import datetime



class RegisterUser(BaseModel):
    user_name: str
    email: EmailStr
    password: str


class ResponseUser(BaseModel):
    id: int
    user_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    @classmethod
    def from_orm(cls, obj):
        return cls(user_name=obj.user_name, created_at=obj.created_at.isoformat())

    class Config:
        from_attributes = True


class ResponseAutorization(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResendEmail(BaseModel):
    email: EmailStr


class RequestForgotPassword(BaseModel):
    email: EmailStr


class SuccesMessage(BaseModel):
    success: bool
    status_code: int
    message: str


class ResetForgotPassword(BaseModel):
    reset_password_token: str
    new_password: str
    confirm_password: str


class RequestConfirmEmail(BaseModel):
    email_token: str

class DonwloadFile(BaseModel):
    user_id:int
    file_name:str
    