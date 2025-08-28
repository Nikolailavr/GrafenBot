import asyncio
import datetime
import logging
import random

from apps.sender.bot.main_bot import bot
from apps.sender.google_client import GoogleClient
from apps.sender.misc import const

from core.config import settings


logger = logging.getLogger(__name__)
date_format = '%d-%m-%Y'


async def check_mess():
    await send_reminder_for_class("0")
    await send_reminder_for_class("2")


async def send_reminder_for_class(class_num: str):
    """
    Отправка напоминания по расписанию на следующий день для конкретного класса
    """
    gclient = GoogleClient()

    # 1. Получаем расписание класса
    schedule = gclient.get_schedule_by_class(class_num)
    if not schedule:
        logger.warning(f"Расписание для Class_{class_num} не найдено")
        return

    # 2. Берем расписание на следующий день
    next_day = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(date_format)
    schedule_map = {row["date"]: row for row in schedule if row.get("date")}

    if data := schedule_map.get(next_day):
        if not data.get("text"):
            return

        # 3. Формируем список telegram_id
        telegram_id = "🍕 "
        if data.get("telegram_id"):
            telegram_id += f'@{data["telegram_id"]}'
        if data.get("telegram_id2"):
            telegram_id += f', @{data["telegram_id2"]}'

        # 4. Формируем сообщение
        mess = const.TEXT_MESS.format(
            date=data["date"],
            text=data["text"],
            telegram_id=telegram_id
        )

        # 5. Отправляем в чат
        await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=mess)
        logger.info(f"{datetime.datetime.now()} - Отправлено сообщение для Class_{class_num} на {next_day}")
    else:
        logger.info(f"{datetime.datetime.now()} - Нет данных на {next_day} для Class_{class_num}")

