import logging
from datetime import datetime

from apps.sender.bot.sent_msg import SentMessage

from core.database.schemas import ClassRead
from core.services import ClassService, ScheduleService
from core.sync_gd import GoogleClient

logger = logging.getLogger(__name__)
date_format = "%d-%m-%Y"


async def check_mess():
    await GoogleClient().sync_google_to_db()
    classes = await ClassService.list_classes()
    for class_ in classes:
        await send_reminder_for_class(class_)


async def send_reminder_for_class(class_: ClassRead):
    """
    Отправка напоминания по расписанию на следующий день для конкретного класса
    """
    schedule = await ScheduleService.get_tomorrow(class_.num)
    if schedule:
        await SentMessage.msg_tomorrow(
            schedule=schedule,
            chat_id=class_.chat_id,
        )

    today = datetime.today()
    if today.isoweekday() == 7:
        week = await ScheduleService.get_week(class_.num, days=5)
        if week:
            await SentMessage.msg_week(
                schedules=week,
                chat_id=class_.chat_id,
            )
