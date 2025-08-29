import logging
from unicodedata import digit

from aiogram import Router, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from apps.sender.bot.sent_msg import SentMessage
from core.config import settings, bot
from core.services import ScheduleService, ClassService
from core.sync_gd import GoogleClient

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("sync"))
async def __sync(message: Message):
    if message.from_user.id != settings.telegram.admin_chat_id:
        return
    await bot.send_message(
        chat_id=settings.telegram.admin_chat_id,
        text="Sync started..",
    )
    await GoogleClient().sync_google_to_db()
    await bot.send_message(
        chat_id=settings.telegram.admin_chat_id,
        text="Sync completed!",
    )


@router.message(Command("tomorrow"))
async def __tomorrow(message: Message, command: CommandObject):
    if message.from_user.id != settings.telegram.admin_chat_id:
        return
    class_num = command.args
    if not isinstance(class_num, int):
        await message.answer("Need class_num")
    class_num = int(class_num)
    schedule = await ScheduleService.get_tomorrow(class_num)
    class_data = await ClassService.get_class(class_num)
    await SentMessage.msg_tomorrow(schedule, class_data.chat_id)


# @router.message(Command("check"))
# async def check_command(message: Message):
#     date_str = message.text.split(' ', 1)[1]
#     try:
#         check_date = datetime.strptime(date_str, "%d-%m-%Y")
#     except (ValueError, TypeError):
#         await bot.reply_to(
#             message,
#             f"Некорректный формат даты {date_str}. Используйте DD-MM-YYYY."
#         )
#         return
#     send_data = await SenderData.get_data_by_days(date_str)
#     if send_data.get(date_str, None):
#         text = send_data.get(date_str)
#     else:
#         text = 'На эту дату нет данных'
#     await bot.send_message(chat_id=message.chat.id, text=text)


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
