from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const


async def send_welcome(message: Message, bot: AsyncTeleBot):
    await bot.send_message(chat_id=message.chat.id,
                           text=const.TEXT_WELCOME)


async def week_schedule(message: Message, bot: AsyncTeleBot):
    send_data = await SenderData.get_data_by_days(count_days=5)
    if send_data:
        mess = 'График на ближайшие 5 дней:'
        for date, value in send_data.items():
            mess += f'\n{date} - {value["text"]}'
            # if value["telegram_id"]:
            #     mess += f' (@{value["telegram_id"]})'
        await bot.send_message(chat_id=message.chat.id,
                               text=mess)


async def children_schedule(message: Message, bot: AsyncTeleBot):
    mess = 'К сожалению, нет данных'
    telegram_id = message.from_user.username
    first_name = message.from_user.first_name
    if telegram_id != '':
        send_data = await SenderData.get_data_by_child(telegram_id)
        if send_data:
            mess = f'Уважаемый {first_name}!\n' if first_name else ''
            mess += 'Ваш график на учебный год:'
            for date, value in send_data.items():
                mess += f'\n{value["date"]} - {value["text"]}'
        else:
            mess += f' для @{telegram_id}'
    else:
        mess = 'К сожалению, не смог найти ваше имя пользователя (username) в telegram'
    await bot.send_message(chat_id=message.chat.id,
                           text=mess)
