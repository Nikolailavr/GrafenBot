import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from apps.sender.bot.sender_data import SenderData
from apps.sender.google_client import GoogleClient
from apps.sender.misc import const

from core.config import bot

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
    username = message.from_user.username
    first_name = message.from_user.first_name

    if not username:
        await bot.send_message(message.chat.id,
                               "К сожалению, не смог найти ваше имя пользователя (username) в telegram")
        return

    # 1. Получаем номер класса
    gclient = GoogleClient()
    class_num = gclient.get_user_class(username)
    if not class_num:
        await bot.send_message(message.chat.id,
                               f"Не нашёл данных или класс не указан для @{username}")
        return

    # 2. Получаем расписание
    schedule_data = gclient.get_schedule_by_class(class_num)
    if not schedule_data:
        await bot.send_message(message.chat.id,
                               f"Не найдено расписания для Class_{class_num}")
        return

    # 3. Формируем сообщение
    mess = f'Уважаемый {first_name}!\n' if first_name else ''
    mess += f'Ваш график на учебный год (Class {class_num}):'
    for row in schedule_data:
        mess += f'\n{row["date"]} - {row["text"]}'

    await bot.send_message(chat_id=message.chat.id, text=mess)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
