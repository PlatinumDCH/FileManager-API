from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import backend.app.db.models.base_model as base
import backend.app.db.models.user_model as user


class Files(base.BaseModel):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=True
)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # connect with User
    user: Mapped["user.User"] = relationship(
        "User", back_populates="files", lazy="joined"
    )
