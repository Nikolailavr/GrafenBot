from asgiref.sync import sync_to_async
from telebot.asyncio_filters import SimpleCustomFilter

from apps.sender.models import Admin


@sync_to_async
def get_admins():
    admins = set()
    for admin in Admin.objects.all():
        admins.add(admin.user_id)
    return admins


class AdminFilter(SimpleCustomFilter):
    """
    Filter for admin users
    """
    key = 'admin'

    async def check(self, message):
        return int(message.from_user.id) in await get_admins()
