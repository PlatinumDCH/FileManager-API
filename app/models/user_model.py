from sqlalchemy import String, Enum
from sqlalchemy.orm import  mapped_column, Mapped, relationship
from sqlalchemy import (String, Boolean, DateTime, func)

from app.config.pack_roles import RoleSet              
import app.models.base_model as base
import app.models.token_model as token

class User(base.BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    role: Mapped[RoleSet] = mapped_column(Enum(RoleSet), default=RoleSet.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    tokens: Mapped[list["token.UserTokens"]] = relationship("UserTokens", back_populates="user")