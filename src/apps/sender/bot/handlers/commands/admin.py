from datetime import datetime
import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const
from core.config import settings, bot

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("check"))
async def check_command(message: Message):
    date_str = message.text.split(' ', 1)[1]
    try:
        check_date = datetime.strptime(date_str, "%d-%m-%Y")
    except (ValueError, TypeError):
        await bot.reply_to(
            message,
            f"Некорректный формат даты {date_str}. Используйте DD-MM-YYYY."
        )
        return
    send_data = await SenderData.get_data_by_days(date_str)
    if send_data.get(date_str, None):
        text = send_data.get(date_str)
    else:
        text = 'На эту дату нет данных'
    await bot.send_message(chat_id=message.chat.id, text=text)


@router.message(Command("test"))
async def test_command(message: Message):
    await bot.send_message(chat_id=settings.telegram.admin_chat_id,
                           text=const.TEXT_WELCOME)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)