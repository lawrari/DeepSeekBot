from typing import Literal

from sqlalchemy.dialects.postgresql import insert

from services.database.models import Usage
from services.database.repo.base import BaseRepo


class UsagesRepo(BaseRepo):
    async def add_usage(
        self,
        profile_id: int,
        request_type: Literal["Text", "Image"],
        input_tokens_used: float,
        output_tokens_used: float,
        yandex_input_tokens_used: float,
        yandex_output_tokens_used: float,
        seconds_spent_on_request: int
    ):

        usage_insert_stmt = (
            insert(Usage)
            .values(
                profile_id=profile_id,
                request_type=request_type,
                input_tokens_used=input_tokens_used,
                output_tokens_used=output_tokens_used,
                yandex_input_tokens_used=yandex_input_tokens_used,
                yandex_output_tokens_used=yandex_output_tokens_used,
                seconds_spent_on_request=seconds_spent_on_request
            ).returning(Usage))
        
        result = await self.session.execute(usage_insert_stmt)
        usage = result.scalar_one()

        await self.session.commit()
        return usage
    
    
