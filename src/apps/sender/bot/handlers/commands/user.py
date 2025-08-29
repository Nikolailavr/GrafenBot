import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from apps.sender.google_client import GoogleClient
from apps.sender.misc import const

from core.config import bot

logger = logging.getLogger(__name__)
router = Router()


async def get_user_classes(message: Message) -> list[str] | None:
    username = message.from_user.username
    if not username:
        await bot.send_message(message.chat.id, "Не найден username в Telegram")
        return None

    classes = GoogleClient().get_user_classes(username)
    if not classes:
        await bot.send_message(message.chat.id, f"Не найдено классов для @{username}")
        return None

    return classes


@router.message(Command("start"))
async def send_welcome(message: Message):
    await bot.send_message(chat_id=message.chat.id, text=const.TEXT_WELCOME)


@router.message(Command("week"))
async def week_schedule(message: Message):
    classes = await get_user_classes(message)
    if not classes:
        return

    gclient = GoogleClient()
    mess = "График на ближайшие 5 дней:"

    for class_num in classes:
        send_data = gclient.get_for_days(class_num)
        if send_data:
            mess += f"\n\nКласс {class_num}:"
            for date, value in send_data.items():
                mess += f'\n{date} - {value["text"]}'

    await bot.send_message(chat_id=message.chat.id, text=mess)


@router.message(Command("my_schedule"))
async def children_schedule(message: Message):
    classes = await get_user_classes(message)
    if not classes:
        return

    gclient = GoogleClient()
    first_name = message.from_user.first_name or ""
    mess = f"Уважаемый {first_name}!\nВаш график на учебный год:"

    for class_num in classes:
        user_schedule = gclient.get_user_schedule(class_num, message.from_user.username)
        mess += f"\n\nКласс {class_num}:"
        mess += gclient.format_schedule(user_schedule, "")

    await bot.send_message(chat_id=message.chat.id, text=mess)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
