import asyncio
import datetime
import logging
import random

from apps.sender.bot.main_bot import bot
from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const

from core import settings


logger = logging.getLogger(__name__)
date_format = '%d-%m-%Y'


async def check_mess():
    schedule = await SenderData.get_all_schedule()
    await send_birthday(schedule)
    await send_reminder(schedule)


async def send_reminder(schedule: dict):
    logger.info(f'{datetime.datetime.now()} - Запуск расписания выполнен')
    date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
    if data := schedule.get(date, dict()):
        if data.get('text'):
            telegram_id = '🍕 '
            if data['telegram_id']:
                telegram_id += f'@{data["telegram_id"]}'
            if data['telegram_id2']:
                telegram_id += f', @{data["telegram_id2"]}'
            mess = const.TEXT_MESS.format(date=data['date'],
                                          text=data['text'],
                                          telegram_id=telegram_id)
            await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                                   text=mess)


async def send_birthday(schedule: dict):
    datenow = datetime.datetime.now().strftime(date_format)
    if data := schedule.get(datenow, dict()):
        if data.get('event', None):
            num = random.randint(0, 9)
            mess = const.BIRTHDAY[num].format(name=data.get('name', ''))
            await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                                   text=mess)
            await asyncio.sleep(30)
