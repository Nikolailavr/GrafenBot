from apps.sender.bot.main_bot import bot
from apps.sender.bot.sender_data import SenderData

from core import settings


async def send_to_all_subscribers():
    send_data = await SenderData.get_data()
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID,
                           text=send_data['text'])

