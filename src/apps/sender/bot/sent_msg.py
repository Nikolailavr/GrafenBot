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

def _convert_date(date: str, need_week: bool = False) -> str:
    converted_date = datetime.strptime(date, date_format_db)
    weekday = WEEKDAYS_RU[converted_date.weekday()]
    day = converted_date.day
    month = MONTHS_RU[converted_date.month - 1]
    year = converted_date.year
    if need_week:
        return f"{weekday},\n📅 {day} {month} {year}"
    else:
        return f"{day} {month} {year}"

def _choose_mess(schedule: ScheduleRead):
    text = schedule.child.lower()

    # 1. Собираем список доступных юзернеймов (отбрасываем None и пустые строки)
    usernames = []
    if schedule.mother:
        usernames.append(f"@{schedule.mother}")
    if schedule.father:
        usernames.append(f"@{schedule.father}")

    # Текст-предупреждение, если контактов нет вообще
    no_contacts_warning = "\n⚠️ У родителей не указан @username! Пожалуйста, передайте им информацию."

    # 2. Формируем сообщение
    if "пицца" in text or "пиццы" in text:
        # День пиццы
        mess = (
            "🍕 🍕 🍕 🍕 🍕\n"
            "УРА! Завтра день ПИЦЦЫ!\n"
            "📲 Не забудьте заказать ПИЦЦУ\n"
        )
        # Если есть хотя бы один юзернейм, добавляем их через пробел
        if usernames:
            mess += " ".join(usernames)
        else:
            mess += no_contacts_warning

    else:
        # Обычное сообщение про перекус
        mess = (
            "🍎 🍊 🍌 🍏 🫐 🍉 🍇\n\n"
            f"📅 Завтра в {_convert_date(schedule.date, need_week=True)}\n"
            "🥪 Перекус приносит:\n"
            f"👉 {schedule.child}\n"
        )
        # Если есть хотя бы один юзернейм, добавляем их через запятую
        if usernames:
            mess += f"📲 {', '.join(usernames)}"
        else:
            mess += no_contacts_warning

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
