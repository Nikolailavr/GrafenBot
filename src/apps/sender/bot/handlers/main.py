from aiogram import Dispatcher

from apps.sender.bot.handlers.commands import (
    register_users_handlers,
    register_admin_handlers,
)


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_users_handlers,
    )
    for handler in handlers:
        handler(dp)
