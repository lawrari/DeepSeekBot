from sqlalchemy import BIGINT, NUMERIC, TEXT, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin, TableNameMixin


class Subscription(Base, TimestampMixin, TableNameMixin):
    subscription_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    requests_amount: Mapped[int] = mapped_column(BIGINT)
    image_requests_amount: Mapped[int] = mapped_column(BIGINT)
    price: Mapped[float] = mapped_column(NUMERIC)
    description: Mapped[str] = mapped_column(TEXT)

    def __repr__(self):
        return f"<Subscription {self.subscription_id}>"
