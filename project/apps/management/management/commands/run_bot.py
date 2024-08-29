import asyncio
import datetime
import logging

import schedule
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.sender.bot.main_bot import bot
from apps.sender.bot.sender import send_reminder

logger = logging.getLogger(__name__)


async def schedule_run():
    logger.info(f"{datetime.datetime.now()} | INFO - Schedule start")
    (schedule.every().day
     .at(settings.TIME_TO_SEND, settings.TIME_ZONE)
     .do(lambda: asyncio.create_task(send_reminder()))
     )
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def start():
    await asyncio.gather(
        schedule_run(),
        bot.infinity_polling(logger_level=logging.DEBUG)
    )


class Command(BaseCommand):
    help = "Запуск бота"

    def handle(self, *args, **options):
        print(settings.TELEGRAM_TOKEN)
        asyncio.run(start())
