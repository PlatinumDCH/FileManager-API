from sqlalchemy import String, Enum
from sqlalchemy.orm import  mapped_column, Mapped, relationship
from sqlalchemy import (String, Boolean, DateTime, func)

from backend.app.utils.pack_roles import RoleSet              
import backend.app.db.models.base_model as base
import backend.app.db.models.token_model as token
import backend.app.db.models.files_model as user_files

class User(base.BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    role: Mapped[RoleSet] = mapped_column(Enum(RoleSet), default=RoleSet.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    tokens: Mapped[list["token.UserTokens"]] = relationship("UserTokens", back_populates="user")
    files: Mapped[list["user_files.Files"]] = relationship("Files", back_populates="user", cascade="all, delete-orphan")