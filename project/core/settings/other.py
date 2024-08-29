from core.settings.default import env

TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = env.int('TELEGRAM_CHAT_ID')
TIME_TO_SEND = env.str('TIME_TO_SEND')
LOG_LEVEL = env.str('LOG_LEVEL')
