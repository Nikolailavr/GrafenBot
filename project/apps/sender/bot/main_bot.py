import telebot
from telebot.async_telebot import AsyncTeleBot
from django.conf import settings

from apps.sender.bot.filters.admin import AdminFilter
from apps.sender.bot.handlers.commands.admin import check_command
from apps.sender.bot.handlers.commands.user import (
    send_welcome
)

bot = AsyncTeleBot(
    settings.TELEGRAM_TOKEN,
    parse_mode='HTML'
)

telebot.logger.setLevel(settings.LOG_LEVEL)

# Обработчики сообщений
bot.register_message_handler(
    send_welcome, commands=['start'], pass_bot=True)
bot.register_message_handler(
    check_command, commands=['check'], pass_bot=True, admin=True)


# Фильтр для администраторов
bot.add_custom_filter(AdminFilter())
