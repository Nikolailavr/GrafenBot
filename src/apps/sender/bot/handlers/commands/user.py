import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from apps.sender.bot.sent_msg import SentMessage
from apps.sender.misc import const

from core.config import bot
from core.services import ScheduleService

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def send_welcome(message: Message):
    await bot.send_message(chat_id=message.chat.id, text=const.TEXT_WELCOME)


@router.message(Command("week"))
async def week_schedule(message: Message):
    username = message.from_user.username
    if username:
        classes = await ScheduleService.get_class_parents(username)
        for class_ in classes:
            schedules = await ScheduleService.get_week(class_, days=5)
            if schedules:
                await SentMessage.msg_week(schedules, message.chat.id)


@router.message(Command("my_schedule"))
async def children_schedule(message: Message):
    username = message.from_user.username
    if not username:
        await message.answer("Не найден username в Telegram")
        return

    # 1. Берём все расписания для данного родителя
    schedules = await ScheduleService.get_by_parents(username)
    if not schedules:
        await message.answer("У вас нет зарегистрированных детей с расписанием.")
        return
    await SentMessage.msg_schedule(schedules, message.chat.id)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
