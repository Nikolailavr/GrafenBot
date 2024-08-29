from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from apps.sender.bot.sender_data import SenderData


async def send_welcome(message: Message, bot: AsyncTeleBot):
    await bot.reply_to(message, text='Приветствую! Я бот, который отправляет напоминание о перекусах первоклассников!')


async def week_schedule(message: Message, bot: AsyncTeleBot):
    send_data = await SenderData.get_data(count_days=5)
    if send_data:
        mess = 'График на ближайшие 5 дней:'
        for date, value in send_data.items():
            mess += f'\n{date} - {value["text"]}'
            if value["telegram_id"]:
                mess += f'(@{value["telegram_id"]})'
        await bot.send_message(chat_id=message.chat.id,
                               text=mess)


async def children_schedule(message: Message, bot: AsyncTeleBot):
    telegram_id = message.text.split(' ', 1)[1]
    send_data = await SenderData.get_data()
    if send_data:
        mess = 'Ваш график на учебный год:'
        for date, value in send_data.items():
            if value.get('telegram_id') == telegram_id:
                mess += f'\n{value["date"] - value["text"]}'
        await bot.send_message(chat_id=message.chat.id,
                               text=mess)
