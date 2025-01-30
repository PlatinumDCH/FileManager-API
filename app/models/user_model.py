from sqlalchemy import String
from sqlalchemy.orm import  mapped_column, Mapped
from sqlalchemy import (String, Boolean, DateTime, func)
                         
import app.models.base_model as base

class User(base.BaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column( String(150), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())