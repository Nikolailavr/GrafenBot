

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def send_welcome(message: Message, bot: AsyncTeleBot):
    await bot.reply_to(message, text='Приветствую! Я бот, который отправляет напоминание о перекусах первоклассников!')

