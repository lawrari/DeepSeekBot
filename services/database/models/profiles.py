from typing import List

from sqlalchemy import BIGINT
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin, TableNameMixin


class Profile(Base, TimestampMixin, TableNameMixin):
    profile_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), unique=True)
    user: Mapped["User"] = relationship("User", back_populates="profile")
    text_requests: Mapped[int] = mapped_column(BIGINT, default=0)
    image_requests: Mapped[int] = mapped_column(BIGINT, default=0)

    usages: Mapped[list["Usage"]] = relationship("Usage", back_populates="profile", foreign_keys="[Usage.profile_id]", uselist=True)

    def __repr__(self):
        return f"<Profile {self.profile_id} {self.user_id}>"
