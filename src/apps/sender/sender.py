import logging
from datetime import datetime

from apps.sender.bot.sent_msg import SentMessage
from core import settings
from core.config import bot

from core.database.schemas import ClassRead
from core.services import ClassService, ScheduleService
from core.sync_gd import GoogleClient

logger = logging.getLogger(__name__)
date_format = "%d-%m-%Y"


async def check_mess():
    try:
        await GoogleClient().sync_google_to_db()
        classes = await ClassService.list_classes()
        for class_ in classes:
            await send_reminder_for_class(class_)
    except Exception as ex:
        await bot.send_message(
            chat_id=settings.telegram.admin_chat_id,
            text=f'Не удалось отправить уведомление:'
                 f'Ошибка: {ex}',
        )


async def send_reminder_for_class(class_: ClassRead):
    """
    Отправка напоминания по расписанию на следующий день для конкретного класса
    """
    try:
        schedule = await ScheduleService.get_tomorrow(class_.num)
        if schedule:
            await SentMessage.msg_tomorrow(
                schedule=schedule,
                chat_id=class_.chat_id,
            )
    except Exception as ex:
        await bot.send_message(
            chat_id=settings.telegram.admin_chat_id,
            text=f'Ошибка при уведомлении на завтра (Класс {class_.num})',
        )
        raise ex

    today = datetime.today()
    if today.isoweekday() == 7 and class_.num != 4:
        days = 5 if class_.num < 4 else 6
        try:
            week = await ScheduleService.get_week(class_.num, days=days)
            if week:
                await SentMessage.msg_week(
                    schedules=week,
                    chat_id=class_.chat_id,
                )
        except Exception as ex:
            await bot.send_message(
                chat_id=settings.telegram.admin_chat_id,
                text=f'Ошибка при уведомлении на неделю (Класс {class_.num})',
            )
            raise ex