import asyncio
import logging

from core.database.schemas import ClassCreate, FamilyCreate, ScheduleCreate

import gspread

from core.config import BASE_DIR
from core.services import ClassService, FamilyService, ScheduleService

CREDS = BASE_DIR / "creds.json"
date_format = "%d-%m-%Y"
logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    async def sync_google_to_db(self):
        await self._sync_classes()
        await self._sync_families()
        await self._sync_schedules()

    async def _sync_classes(self):
        classes_data = await asyncio.to_thread(
            lambda: self.sh.worksheet("Config").get_all_records()
        )

        for row in classes_data:
            class_in = ClassCreate(
                num=int(row.get("class")), chat_id=row.get("chat_id")
            )
            # Создаём или обновляем через сервис
            existing = await ClassService.get_class(class_in.num)
            if existing:
                await ClassService.update_class(class_in)
            else:
                await ClassService.create_class(class_in)

        logger.info("Classes synced")

    async def _sync_families(self):
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

            existing_family = await FamilyService.get_family(child=row.get("family"))
            if existing_family:
                await FamilyService.update_family(row.get("family"), family_in)
            else:
                await FamilyService.create_family(family_in)

        logger.info("Families synced")

    async def _sync_schedules(self):
        classes = await ClassService.list_classes()

        for class_obj in classes:
            schedule_rows = await asyncio.to_thread(
                lambda: self.get_schedule_by_class(class_obj.num)
            )

            for row in schedule_rows:
                date = row.get("date")
                if not date:
                    continue

                child = row.get("text")
                family = await FamilyService.get_family(child=child)

                schedule_in = ScheduleCreate(
                    date=date,
                    child_id=family.id,
                )

                # Сохраняем через сервис
                existing_schedule = await ScheduleService.list_schedules(
                    child_id=family.id
                )
                exists_for_date = next(
                    (s for s in existing_schedule if s.date == date), None
                )
                if exists_for_date:
                    await ScheduleService.update_schedule(
                        exists_for_date.id, schedule_in
                    )
                else:
                    await ScheduleService.create_schedule(schedule_in)

        logger.info("Schedules synced")

    def get_schedule_by_class(self, class_num: int) -> list[dict]:
        try:
            ws_class = self.sh.worksheet(f"Class_{class_num}")
        except gspread.exceptions.WorksheetNotFound:
            return []
        return ws_class.get_all_records()


# -----------------------
# Тестовый запуск
# -----------------------
if __name__ == "__main__":
    asyncio.run(GoogleClient().sync_google_to_db())
