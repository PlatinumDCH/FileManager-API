from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    user_name: str
    email: EmailStr
    password_plain: str = Field(..., min_length=4)

class ShowUser(BaseModel):
    id:int
    user_name:str
    email: EmailStr
    is_active: bool

    class Config():
        from_attributes = True