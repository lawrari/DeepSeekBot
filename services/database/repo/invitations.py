from sqlalchemy.dialects.postgresql import insert

from services.database.models import Invitation
from services.database.repo.base import BaseRepo


class InvitationsRepo(BaseRepo):
    async def create_invitation(
        self,
        inviter: int,
        invitee: int,
    ):
        insert_stmt = (
            insert(Invitation)
            .values(
                inviter_id=inviter,
                invitee_id=invitee
            )
            .on_conflict_do_nothing(index_elements=[Invitation.invitee_id])
            .returning(Invitation)
        )

        result = await self.session.execute(insert_stmt)
        

        invitation = result.scalar_one()

        await self.session.commit()
        return invitation
