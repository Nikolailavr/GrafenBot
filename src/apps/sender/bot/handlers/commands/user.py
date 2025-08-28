import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const

from core.config import settings, bot

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def send_welcome(message: Message):
    await bot.send_message(chat_id=message.chat.id,
                           text=const.TEXT_WELCOME)


@router.message(Command("week"))
async def week_schedule(message: Message):
    send_data = await SenderData.get_for_days(count_days=5)
    if send_data:
        mess = 'График на ближайшие 5 дней:'
        for date, value in send_data.items():
            mess += f'\n{date} - {value["text"]}'
        await bot.send_message(chat_id=message.chat.id,
                               text=mess)


@router.message(Command("my_schedule"))
async def children_schedule(message: Message):
    mess = 'К сожалению, нет данных'
    telegram_id = message.from_user.username
    first_name = message.from_user.first_name
    if telegram_id != '':
        send_data = await SenderData.get_by_child(telegram_id)
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


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
