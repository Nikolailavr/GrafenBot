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

class ScheduleStates(StatesGroup):
    waiting_for_tomorrow_class = State()
    waiting_for_week_class = State()



@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Команда для отмены любого текущего действия"""
    current_state = await state.get_state()
    if current_state is None:
        return  # Если отменять нечего, просто игнорируем

    await state.clear()
    await message.answer("Действие отменено. ❌")


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

# ==========================================
# ЛОГИКА ДЛЯ /tomorrow
# ==========================================
@router.message(Command("tomorrow"))
async def cmd_tomorrow_start(message: Message, state: FSMContext):
    """Шаг 1: Получаем команду и просим номер класса"""
    if message.from_user.id != settings.telegram.admin_chat_id:
        return

    await message.answer("Введите номер класса (или /cancel для отмены):")
    # Переводим бота в режим ожидания ввода для tomorrow
    await state.set_state(ScheduleStates.waiting_for_tomorrow_class)


@router.message(ScheduleStates.waiting_for_tomorrow_class)
async def process_tomorrow_class(message: Message, state: FSMContext):
    """Шаг 2: Ловим введенный текст и обрабатываем его"""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число или нажмите /cancel")
        return

    class_num = int(message.text)

    # Очищаем состояние, чтобы бот больше не ждал класс
    await state.clear()

    # Выполняем вашу логику
    schedule = await ScheduleService.get_tomorrow(class_num)
    class_data = await ClassService.get_class(class_num)

    if schedule:
        # В зависимости от того, как работает get_class (возвращает список или 1 объект)
        for class_ in class_data:
            await SentMessage.msg_tomorrow(schedule, class_.chat_id)
        await message.answer(f"✅ Уведомления 'Завтра' для {class_num} класса отправлены.")
    else:
        await message.answer(f"Завтра нет перекусов для {class_num} класса.")


# ==========================================
# ЛОГИКА ДЛЯ /testweek
# ==========================================
@router.message(Command("testweek"))
async def cmd_testweek_start(message: Message, state: FSMContext):
    """Шаг 1: Получаем команду и просим номер класса"""
    if message.from_user.id != settings.telegram.admin_chat_id:
        return

    await message.answer("Введите номер класса для недели (или /cancel для отмены):")
    await state.set_state(ScheduleStates.waiting_for_week_class)


@router.message(ScheduleStates.waiting_for_week_class)
async def process_week_class(message: Message, state: FSMContext):
    """Шаг 2: Ловим введенный текст и обрабатываем его"""
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите число или нажмите /cancel")
        return

    class_num = int(message.text)

    # Очищаем состояние
    await state.clear()

    days = 5 if class_num < 4 else 6
    schedules = await ScheduleService.get_week(class_num, days=days)
    class_data = await ClassService.get_class(class_num)
    logger.info(class_data)

    if schedules and class_data:
        for c in class_data:
            await SentMessage.msg_week(schedules, c.chat_id)
        await message.answer(f"✅ Уведомления 'Неделя' для {class_num} класса отправлены.")
    else:
        await message.answer(f"Нет данных на неделю для {class_num} класса.")


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
