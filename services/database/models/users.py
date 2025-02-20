from typing import Optional

from sqlalchemy import String
from sqlalchemy import text, BIGINT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin, TableNameMixin


class User(Base, TimestampMixin, TableNameMixin):
    user_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128))
    language: Mapped[str] = mapped_column(String(10), server_default=text("'en'"))
    
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    referrals: Mapped[list["Invitation"]] = relationship("Invitation", back_populates="inviter", foreign_keys="Invitation.inviter_id", cascade="all, delete-orphan", lazy='selectin')

    def __repr__(self):
        return f"<{self.role} {self.user_id} {self.username} {self.full_name}>"
