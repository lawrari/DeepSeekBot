from sqlalchemy import update, select

from services.database.models import Profile
from services.database.repo.base import BaseRepo


class ProfilesRepo(BaseRepo):
    async def get_profile(
        self,
        user_id: int
    ) -> Profile:
        select_stmt = select(Profile).where(Profile.user_id==user_id)

        result = await self.session.execute(select_stmt)
        profile = result.scalar_one()

        await self.session.commit()
        return profile
    
    async def add_requests(
            self,
            profile_id,
            requests_amount,
            image_requests_amount
    ) -> Profile:
        update_stmt = update(Profile).where(Profile.profile_id == profile_id).values(text_requests=Profile.text_requests+requests_amount, 
                                                                                     image_requests=Profile.image_requests+image_requests_amount).returning(Profile)
        result = await self.session.execute(update_stmt)
        profile = result.scalar_one()

        await self.session.commit()
        return profile
