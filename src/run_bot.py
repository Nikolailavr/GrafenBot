import asyncio
import datetime
import logging

import schedule

from apps.sender.bot.main_bot import bot, start_bot
from apps.sender.bot.sender import check_mess
from core.config import settings

logger = logging.getLogger(__name__)


async def schedule_run():
    logger.info(f"{datetime.datetime.now()} | INFO - Schedule start")
    (schedule.every().day
     .at(settings.time.time_to_send, settings.time.time_zone)
     .do(lambda: asyncio.create_task(check_mess()))
     )
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def start():
    await asyncio.gather(
        schedule_run(),
        start_bot(),
    )


