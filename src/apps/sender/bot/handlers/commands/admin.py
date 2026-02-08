import logging

from aiogram import Router, Dispatcher, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from apps.sender.bot.sent_msg import SentMessage
from apps.sender.bot.services.delete_msg import delete_by_link
from apps.sender.sender import check_mess
from core.config import settings, bot
from core.services import ScheduleService, ClassService
from core.sync_gd import GoogleClient

logger = logging.getLogger(__name__)
router = Router()

class DeleteMessageStates(StatesGroup):
    waiting_for_link = State()  # Состояние ожидания ссылки


@router.message(DeleteMessageStates.waiting_for_link, Command("cancel"))
async def cancel_delete(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Удаление отменено.")


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
    class_data = await ClassService.get_class(class_num)
    if schedule:
        for class_ in class_data:
            await SentMessage.msg_tomorrow(schedule, class_.chat_id)
    else:
        await message.answer("Завтра нет перекусов")


@router.message(Command("testweek"))
async def __week(message: Message, command: CommandObject):
    if message.from_user.id != settings.telegram.admin_chat_id:
        return
    class_num = command.args
    if class_num is None:
        await message.answer("Укажите номер класса через пробел")
    if not class_num.isdigit():
        await message.answer("Номер класса должен быть числом")
    class_num = int(class_num)
    days = 5 if class_num < 4 else 6
    schedules = await ScheduleService.get_week(class_num, days=days)
    class_ = await ClassService.get_class(class_num)
    if schedules and class_:
        for c in class_:
            await SentMessage.msg_week(schedules, c.chat_id)


@router.message(Command("test"))
async def __test(message: Message):
    if message.from_user.id != settings.telegram.admin_chat_id:
        return
    await check_mess()


@router.message(Command("delete"))
async def __delete(message: Message, state: FSMContext):
    # Проверка на админа (замените на вашу логику)
    if message.from_user.id != settings.telegram.admin_chat_id:
        return

    await message.answer("Пришлите ссылку на сообщение, которое нужно удалить.")
    # Устанавливаем состояние ожидания
    await state.set_state(DeleteMessageStates.waiting_for_link)

# 2. Ожидание ввода ссылки
@router.message(DeleteMessageStates.waiting_for_link, F.text)
async def process_delete_by_link(message: Message, state: FSMContext):
    link = message.text.strip()

    # Вызываем метод удаления (который мы написали ранее)
    success = await delete_by_link(message.bot, link)

    if success:
        await message.answer("✅ Сообщение успешно удалено!")
    else:
        await message.answer("❌ Не удалось удалить. Проверьте ссылку или права бота в том чате.")

    # Сбрасываем состояние, чтобы бот перестал ждать ссылку
    await state.clear()

def register_admin_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
