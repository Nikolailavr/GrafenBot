import asyncio
import datetime
import logging

import schedule

from apps.sender.bot.main_bot import start_bot
from apps.sender.bot.sender import check_mess
from core.config import settings

logger = logging.getLogger(__name__)


async def schedule_run():
    logger.info(f"{datetime.datetime.now()} | INFO - Schedule start")
    (schedule.every().day
     .at(settings.schedule.time_to_send, settings.schedule.time_zone)
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


def main():
    logger.info("Запускаем бота с расписанием")
    asyncio.run(start())


if __name__ == "__main__":
    main()