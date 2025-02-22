from .admins import admin_start_router
from .users import maintenance_router, user_start_router, referral_start_router, request_router, payments_router


routers_list = [
    admin_start_router,
    maintenance_router,
    referral_start_router,
    user_start_router,
    payments_router,
    request_router,
]

__all__ = [
    'routers_list',
]
