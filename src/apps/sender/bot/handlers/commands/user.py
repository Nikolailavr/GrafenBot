import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

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
    """Показать расписание на ближайшие 5 дней"""
    schedules = await ScheduleService.get_week(
        username=message.from_user.username, days=5
    )

    if not schedules:
        await message.answer("У вас нет расписания на ближайшую неделю.")
        return

    mess = "📅 График на ближайшие 5 дней:"

    # группируем по классу и дате
    grouped = {}
    for s in schedules:
        class_num = s.family.class_num if s.family else "?"
        child = s.family.child if s.family else "?"
        key = f"{class_num} ({child})"
        if key not in grouped:
            grouped[key] = {}
        if s.date not in grouped[key]:
            grouped[key][s.date] = []
        grouped[key][s.date].append(s.text or "")

    # формируем вывод
    for class_info, days in grouped.items():
        mess += f"\n\nКласс {class_info}:"
        for date, lessons in days.items():
            for lesson in lessons:
                mess += f"\n{date} — {lesson}"

    await message.answer(mess)


@router.message(Command("my_schedule"))
async def children_schedule(message: Message):
    username = message.from_user.username
    first_name = message.from_user.first_name or ""

    schedules = await ScheduleService.get_week(username, days=5)

    if not schedules:
        await message.answer("У вас нет зарегистрированного расписания.")
        return

    mess = f"Уважаемый {first_name}!\nВаш график на ближайшую неделю:"

    current_date = None
    for s in schedules:
        if s.date != current_date:  # группировка по датам
            mess += f"\n\n📅 {s.date}:"
            current_date = s.date
        mess += f"\n— {s.text or ''}"

    await message.answer(mess)


def register_users_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
