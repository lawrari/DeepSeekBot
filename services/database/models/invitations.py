from sqlalchemy import BIGINT, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin, TableNameMixin


class Invitation(Base, TimestampMixin, TableNameMixin):
    invitation_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    inviter_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.telegram_id'))
    inviter: Mapped["User"] = relationship("User", foreign_keys=[inviter_id], back_populates="referrals")
    invitee_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.telegram_id'), unique=True)
    invitee: Mapped["User"] = relationship("User", foreign_keys=[invitee_id])

    def __repr__(self):
        return f"<Invitation {self.invitation_id}>"
