import datetime
import logging

from sqlalchemy.util import await_only

from apps.sender.bot.main_bot import bot
from apps.sender.bot.sent_msg import SentMessage
from apps.sender.misc import const

from core.config import settings
from core.database.schemas import ClassRead
from core.services import ClassService, ScheduleService

logger = logging.getLogger(__name__)
date_format = "%d-%m-%Y"


async def check_mess():
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
