from sqlalchemy import String, Enum
from sqlalchemy.orm import  mapped_column, Mapped
from sqlalchemy import (String, Boolean, DateTime, func)

from app.config.pack_roles import RoleSet              
import app.models.base_model as base

class User(base.BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column( String(150), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    role: Mapped[Enum] = mapped_column("role", Enum(RoleSet), default=RoleSet.user, nullable=True)
    confirmed: Mapped["bool"] = mapped_column(Boolean, default=False, nullable=True)