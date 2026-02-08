import re

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest


async def delete_by_link(bot: Bot, link: str) -> bool:
    """
    Удаляет сообщение по ссылке типа https://t.me/c/123456789/551
    Возвращает True, если удалено, False в случае ошибки.
    """
    # Регулярное выражение для извлечения ID чата и ID сообщения
    # Поддерживает форматы /c/ID/MSG и /имя_канала/MSG
    pattern = r"t\.me/(?:c/)?([^/]+)/(\d+)"
    match = re.search(pattern, link)

    if not match:
        print(f"Некорректная ссылка: {link}")
        return False

    chat_part = match.group(1)  # Может быть '2724441831' или 'my_channel'
    message_id = int(match.group(2))

    # Превращаем ID из ссылки в формат, который понимает API (-100...)
    if chat_part.isdigit():
        chat_id = int(f"-100{chat_part}")
    else:
        chat_id = f"@{chat_part}" # Для публичных каналов/групп

    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="!")
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return True
    except TelegramBadRequest as e:
        # Если сообщение уже удалено или бот не админ
        print(f"Ошибка удаления (возможно, сообщение слишком старое): {e}")
        return False
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return False