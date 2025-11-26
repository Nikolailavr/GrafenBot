from datetime import datetime

from core.config import bot
from core.database.schemas import ScheduleRead

date_format_db = "%Y-%m-%d"
date_format = "%d-%m-%Y"


WEEKDAYS_RU = [
    "понедельник", "вторник", "среду",
    "четверг", "пятницу", "субботу", "воскресенье"
]

MONTHS_RU = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]

def _convert_date(date: str) -> str:
    converted_date = datetime.strptime(date, date_format_db)
    weekday = WEEKDAYS_RU[converted_date.weekday()]
    day = converted_date.day
    month = MONTHS_RU[converted_date.month - 1]
    year = converted_date.year
    return f"{weekday}, {day} {month} {year}"

def _choose_mess(schedule: ScheduleRead):
    text = schedule.child.lower()

    # Если в строке ребёнка есть "пицца" или "пиццы"
    if "пицца" in text or "пиццы" in text:
        # День пиццы
        mess = (
            "🍕🍕🍕 УРА! Завтра день ПИЦЦЫ! 🍕🍕🍕\n"
            "📲 Не забудьте заказать ПИЦЦУ"
        )
    else:
        # Обычное сообщение про перекус
        mess = (
            "🍎 🍊 🍌 🍏 🫐 🍉 🍇\n"
            f"📆 Завтра в {_convert_date(schedule.date)}\n"
            "🥪 Перекус приносит:\n"
            f"👉 {schedule.child}\n"
            f"📲 @{schedule.mother}"
        )
        if schedule.father:
            mess += f", @{schedule.father}"
    return mess


class SentMessage:
    @staticmethod
    async def msg_week(schedules: dict, chat_id: int):
        if not schedules:
            await bot.send_message(
                chat_id=chat_id,
                text="Нет расписания на ближайшие дни.",
            )
            return
        mess = ""
        for class_num, s in schedules.items():
            days = len(s)
            mess = f"📅 График на ближайшие {days} дней:"
            for item in s:
                mess += f"\n{_convert_date(item.date)} — {item.child}"

        await bot.send_message(
            chat_id=chat_id,
            text=mess,
        )

    @staticmethod
    async def msg_schedule(schedules: dict, chat_id: int, first_name: str = ""):
        if not schedules:
            await bot.send_message(
                chat_id=chat_id,
                text="Нет расписания.",
            )
            return

        mess = f"Уважаемый {first_name}!\n📅 Ваш график на учебный год:"

        for class_num, schedule in schedules.items():
            mess += "\n"
            for item in schedule:
                mess += f"\n{_convert_date(item.date)} — {item.child}"

        await bot.send_message(
            chat_id=chat_id,
            text=mess,
        )


    @staticmethod
    async def msg_tomorrow(schedule: ScheduleRead, chat_id: int):
        await bot.send_message(
            chat_id=chat_id,
            text=_choose_mess(schedule),
        )
