__all__ = (
    "register_admin_handlers",
    "register_users_handlers",
)

from .user import register_users_handlers
from .admin import register_admin_handlers