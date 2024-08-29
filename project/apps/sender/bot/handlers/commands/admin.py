from datetime import datetime
import logging
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from apps.sender.bot.sender_data import SenderData

logger = logging.getLogger(__name__)


async def check_command(message: Message, bot: AsyncTeleBot):
    date_str = message.text.split(' ', 1)[1]
    try:
        check_date = datetime.strptime(date_str, "%d-%m-%Y")
    except (ValueError, TypeError):
        await bot.reply_to(
            message,
            f"Некорректный формат даты {date_str}. Используйте DD-MM-YYYY."
        )
        return
    send_data = await SenderData.get_data(date_str)
    await bot.send_message(message.from_user.id, text=send_data['text'])
