from datetime import datetime

from core.config import bot

date_format_db = "%Y-%m-%d"
date_format = "%d-%m-%Y"


def _convert_date(date: str) -> str:
    converted_date = datetime.strptime(date, date_format_db)
    return converted_date.strftime(date_format)


class SentMessage:
    @staticmethod
    async def msg_week(schedules: dict, chat_id: int):
        if not schedules:
            await bot.send_message(
                chat_id=chat_id,
                text="Нет расписания на ближайшие дни.",
            )
            return

        mess = f"График на ближайшие 5 дней:"
        for class_num, s in schedules.items():
            mess += f"\n\nКласс {class_num}"
            for item in s:
                mess += f"\n📅 {_convert_date(item.date)} — {item.child}"

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

        mess = f"Уважаемый {first_name}!\nВаш график на учебный год:"

        for class_num, schedule in schedules.items():
            mess += f"\n\nКласс {class_num}:"
            for item in schedule:
                mess += f"\n📅 {_convert_date(item.date)} — {item.child}"

        await bot.send_message(
            chat_id=chat_id,
            text=mess,
        )
