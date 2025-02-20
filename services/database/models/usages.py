from sqlalchemy import BIGINT, NUMERIC, TEXT, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin, TableNameMixin


class Usage(Base, TimestampMixin, TableNameMixin):
    usage_id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)

    profile_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('profiles.profile_id'))
    profile: Mapped["Profile"] = relationship("Profile", back_populates="usages", foreign_keys=[profile_id])

    request_type: Mapped[str] = mapped_column(TEXT)
    input_tokens_used: Mapped[float] = mapped_column(NUMERIC)
    output_tokens_used: Mapped[float] = mapped_column(NUMERIC)
    yandex_input_tokens_used: Mapped[float] = mapped_column(NUMERIC)
    yandex_output_tokens_used: Mapped[float] = mapped_column(NUMERIC)
    seconds_spent_on_request: Mapped[int] = mapped_column(BIGINT) 

    def __repr__(self):
        return f"<Usage {self.usage_id}>"
