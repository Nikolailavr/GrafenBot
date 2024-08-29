import datetime
import logging
from apps.sender.bot.main_bot import bot
from apps.sender.bot.sender_data import SenderData
from apps.sender.misc import const

from core import settings


logger = logging.getLogger(__name__)


async def send_reminder():
    send_data = await SenderData.get_data_by_days()
    logger.info(f'{datetime.datetime.now()} - Запуск расписания выполнен')
    if send_data:
        mess = const.TEXT_MESS.format(date=send_data['date'],
                                      text=send_data['text'],
                                      telegram_id=send_data['telegram_id'])
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                               text=mess)
