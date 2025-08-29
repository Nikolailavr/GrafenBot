import logging

from aiogram import Router, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from apps.sender.bot.sent_msg import SentMessage
from apps.sender.sender import check_mess
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
    if not class_num.isdigit():
        await message.answer("Need class_num")
    class_num = int(class_num)
    schedule = await ScheduleService.get_tomorrow(class_num)
    if schedule:
        class_data = await ClassService.get_class(class_num)
        await SentMessage.msg_tomorrow(schedule, class_data.chat_id)
    else:
        await message.answer("Завтра нет перекусов")

@router.message(Command("test"))
async def __test(message: Message):
    if message.from_user.id != settings.telegram.admin_chat_id:
        return
    await check_mess()

def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
