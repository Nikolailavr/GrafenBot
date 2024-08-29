from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const
from core import settings


async def send_welcome(message: Message, bot: AsyncTeleBot):
    await bot.reply_to(message, text='Приветствую! Я бот, который отправляет напоминание о перекусах первоклассников!')


async def week_schedule(message: Message, bot: AsyncTeleBot):
    send_data = await SenderData.get_data(count_days=5)
    if send_data:
        mess = 'График на ближайшие 5 дней:\n'
        for key, value in send_data.items():
            mess += f'{key} - {value["text"]} (@{value["telegram_id"]})\n'
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                               text=mess)
