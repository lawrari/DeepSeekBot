from typing import Union

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

from services.database.models import User, Profile
from services.database.repo.base import BaseRepo


class UserRepo(BaseRepo):

    async def get_or_create_user_and_profile(
        self,
        telegram_id: int,
        username: Union[str, None],
        full_name: str,
        language: str,
    ):

        insert_stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                language=language,
            )
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_=dict(
                    username=username,
                    full_name=full_name,
                ),
            )
            .returning(User)
        )
        result = await self.session.execute(insert_stmt)
        user = result.scalar_one()

        profile_insert_stmt = (
            insert(Profile)
            .values(user_id=user.user_id)
            .on_conflict_do_nothing(index_elements=[Profile.user_id])
        )
        await self.session.execute(profile_insert_stmt)

        await self.session.commit()
        return user
    

    async def user_exists(self, telegram_id: int) -> bool:
        query = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
    