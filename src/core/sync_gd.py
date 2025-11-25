import asyncio
import datetime
import logging

from core import settings
from core.database.schemas import ClassCreate, FamilyCreate, ScheduleCreate

import gspread

from core.config import BASE_DIR, bot
from core.services import ClassService, FamilyService, ScheduleService

CREDS = BASE_DIR / "creds.json"
date_format = "%d-%m-%Y"
logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    async def sync_google_to_db(self):
        try:
            await self._sync_classes()
            await self._sync_families()
            await self._sync_schedules()
        except Exception as ex:
            logger.error(ex)
            await bot.send_message(
                chat_id=settings.telegram.admin_chat_id,
                text="Ошибка при синхронизации таблицы",
            )

    async def _sync_classes(self):
        await ClassService.delete_table()

        classes_data = await asyncio.to_thread(
            lambda: self.sh.worksheet("Config").get_all_records()
        )

        for row in classes_data:
            class_in = ClassCreate(
                num=int(row.get("class")), chat_id=row.get("chat_id")
            )
            await ClassService.create_class(class_in)

        logger.info("Classes synced")

    async def _sync_families(self):
        await FamilyService.delete_table()

        family_data = await asyncio.to_thread(
            lambda: self.sh.worksheet("Family").get_all_records()
        )

        for row in family_data:
            class_num = int(row.get("class"))

            # Проверяем, что такой класс есть
            existing_class = await ClassService.get_class(class_num)
            if not existing_class:
                continue

            family_in = FamilyCreate(
                child=row.get("family"),
                mother=row.get("username"),
                father=row.get("username2"),
                class_num=class_num,
            )

            await FamilyService.create_family(family_in)

        logger.info("Families synced")

    async def _sync_schedules(self):
        await ScheduleService.delete_table()

        classes = await ClassService.list_classes()

        for class_obj in classes:
            schedule_rows = await asyncio.to_thread(
                lambda: self.get_schedule_by_class(class_obj.num)
            )
            for row in schedule_rows:
                date = row.get("date")
                if date:
                    date = datetime.datetime.strptime(date, date_format)
                    date = date.strftime("%Y-%m-%d")
                else:
                    continue
                try:
                    child = row.get("text")
                    mother = row.get("telegram_id")
                    father = row.get("telegram_id2")
                    schedule_in = ScheduleCreate(
                        date=date,
                        child=child,
                        class_num=class_obj.num,
                        mother=mother,
                        father=father,
                    )
                except Exception as ex:
                    logger.error(
                        "Bad data for %s, date: %s", child, date)
                    await bot.send_message(
                        chat_id=settings.telegram.admin_chat_id,
                        text=f"Недостоверные данные\nТекст: {child}\nДата: {date}\nКласс: {class_obj.num}"
                    )

                await ScheduleService.create_schedule(schedule_in)

        logger.info("Schedules synced")

    def get_schedule_by_class(self, class_num: int) -> list[dict]:
        try:
            ws_class = self.sh.worksheet(f"Class_{class_num}")
        except gspread.exceptions.WorksheetNotFound:
            return []
        return ws_class.get_all_records(expected_headers=["id_", "date", "text", "telegram_id", "telegram_id2"])


# -----------------------
# Тестовый запуск
# -----------------------
if __name__ == "__main__":
    asyncio.run(GoogleClient().sync_google_to_db())
