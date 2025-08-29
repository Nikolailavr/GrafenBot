from datetime import datetime

from core.config import bot

date_format = "%Y-%m-%d"

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
                mess += f"\n📅 {item.date} — {item.child}"

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

        for class_num, items in schedules.items():
            mess += f"\n\nКласс {class_num}:"
            for s, child in sorted(items, key=lambda x: datetime.strptime(x[0].date, date_format)):
                mess += f"\n📅 {s.date} — {s.text or ''} ({child.child})"

        await bot.send_message(
            chat_id=chat_id,
            text=mess,
        )
