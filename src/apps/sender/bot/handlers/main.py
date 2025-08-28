from aiogram import Dispatcher

from apps.sender.bot.handlers.commands.user import register_users_handlers
from apps.sender.bot.handlers.commands.admin import register_admin_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_users_handlers,
    )
    for handler in handlers:
        handler(dp)
