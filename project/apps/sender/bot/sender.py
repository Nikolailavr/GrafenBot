import asyncio
import datetime
import logging
import random

from apps.sender.bot.main_bot import bot
from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const

from core import settings


logger = logging.getLogger(__name__)


async def check_mess():
    schedule = await SenderData.get_data_by_days()
    await send_birthday(schedule)
    await send_reminder(schedule)


async def send_reminder(schedule: dict):
    logger.info(f'{datetime.datetime.now()} - Запуск расписания выполнен')
    if schedule.get('text'):
        mess = const.TEXT_MESS.format(date=schedule['date'],
                                      text=schedule['text'],
                                      telegram_id=schedule['telegram_id'])
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                               text=mess)


async def send_birthday(schedule: dict):
    if schedule.get('event', None):
        num = random.randint(1, 10)
        mess = const.BIRTHDAY[num].format(name=schedule.get('name', ''))
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                               text=mess)
        await asyncio.sleep(30)
