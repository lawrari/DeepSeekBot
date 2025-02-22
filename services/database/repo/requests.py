from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from services.database.repo.users import UserRepo
from services.database.repo.invitations import InvitationsRepo
from services.database.repo.usages import UsagesRepo
from services.database.repo.profiles import ProfilesRepo
from services.database.repo.subscriptions import SubscriptionsRepo
from services.database.repo.payments import PaymentsRepo

@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)
    
    @property
    def invitations(self) -> InvitationsRepo:
        return InvitationsRepo(self.session)
    
    @property
    def usages(self) -> UsagesRepo:
        return UsagesRepo(self.session)
    
    @property
    def profiles(self) -> ProfilesRepo:
        return ProfilesRepo(self.session)
    
    @property
    def subscriptions(self) -> SubscriptionsRepo:
        return SubscriptionsRepo(self.session)
    
    @property
    def payments(self) -> PaymentsRepo:
        return PaymentsRepo(self.session)
