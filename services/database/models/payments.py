from sqlalchemy import BIGINT, FLOAT, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin, TableNameMixin


class Payment(Base, TimestampMixin, TableNameMixin):
    payment_id: Mapped[str] = mapped_column(UUID, primary_key=True, unique=True, nullable=False)

    payer_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("profiles.profile_id"))
    payer: Mapped["Profile"] = relationship("Profile", foreign_keys=[payer_id], lazy='selectin')
    amount: Mapped[float] = mapped_column(FLOAT, nullable=False)
    status: Mapped[str] = mapped_column(String(128), default="pending")
    subscription_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("subscriptions.subscription_id"))
    subscription: Mapped["Subscription"] = relationship("Subscription", foreign_keys=[subscription_id], lazy='selectin')

    def __repr__(self):
        return f"<payment {self.payment_id}>"
