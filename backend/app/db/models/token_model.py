import backend.app.db.models.base_model as base
import backend.app.db.models.user_model as user
from sqlalchemy import (String, ForeignKey)
from sqlalchemy.orm import  mapped_column, Mapped, relationship

class UserTokens(base.BaseModel):
    __tablename__ = "user_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    reset_password_token: Mapped[str] = mapped_column(String(255), nullable=True)
    email_token: Mapped[str] = mapped_column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # connect with User
    user: Mapped["user.User"] = relationship("User", back_populates="tokens",lazy="joined")