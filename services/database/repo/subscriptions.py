from sqlalchemy import select

from services.database.models import Subscription
from services.database.repo.base import BaseRepo


class SubscriptionsRepo(BaseRepo):
    async def get_subscription(
        self,
        subscription_id: int
    ) -> Subscription:

        select_stmt = (
            select(Subscription).where(Subscription.subscription_id==subscription_id)
        )
        
        result = await self.session.execute(select_stmt)
        subscription = result.scalar_one()

        return subscription
