from typing import Literal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update

from services.database.models import Payment
from services.database.repo.base import BaseRepo


class PaymentsRepo(BaseRepo):
    async def create_payment(
            self,
            payment_id,
            payer_id,
            amount,
            subscription_id
    ) -> Payment:
        insert_stmt = (insert(Payment)
                       .values(
                           payment_id=payment_id,
                           payer_id=payer_id,
                           amount=amount,
                           subscription_id=subscription_id
                       )
                       .returning(Payment)
                       )

        result = await self.session.execute(insert_stmt)
        payment = result.scalar_one()

        await self.session.commit()

        return payment
    

    async def change_status(
            self,
            payment_id: str,
            status: Literal['pending', 'succeeded', 'canceled']
    ) -> Payment:
        update_stmt = update(Payment).where(Payment.payment_id==payment_id).values(status=status).returning(Payment)

        result = await self.session.execute(update_stmt)
        payment = result.scalar_one()

        await self.session.commit()
        return payment