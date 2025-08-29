import asyncio
import logging

from sqlalchemy import select, delete

from core.database.db_helper import db_helper
from core.database.models import Class, Family, Schedule
from core.database.schemas import ClassCreate, FamilyCreate, ScheduleCreate

import gspread

from core.config import BASE_DIR

CREDS = BASE_DIR / "creds.json"
date_format = "%d-%m-%Y"
logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    async def sync_google_to_db(self):
        async with db_helper.get_session() as session:
            await self._sync_classes(session)
            await self._sync_families(session)
            await self._sync_schedules(session)

    async def _sync_classes(self, session):
        classes_data = self.sh.worksheet("Config").get_all_records()

        for row in classes_data:
            num = int(row.get("class"))
            chat_id = row.get("chat_id")

            result = await session.execute(select(Class).where(Class.num == num))
            db_class = result.scalars().first()

            if db_class:
                db_class.chat_id = chat_id  # обновляем существующую запись
            else:
                session.add(Class(num=num, chat_id=chat_id))  # создаём новую

        await session.commit()
        logger.info("Table Classes is updated")

    async def _sync_families(self, session):
        family_data = self.sh.worksheet("Family").get_all_records()

        for row in family_data:
            data_dict = {
                "child": row.get("family"),
                "mother": row.get("username"),
                "father": row.get("username2"),
                "class_num": int(row.get("class")),
            }
            family_obj = FamilyCreate.model_validate(data_dict, from_attributes=True)

            result = await session.execute(
                select(Family).where(Family.child == family_obj.child)
            )
            db_family = result.scalars().first()

            if db_family:
                for key, value in family_obj.model_dump().items():
                    setattr(db_family, key, value)
            else:
                session.add(Family(**family_obj.model_dump()))

        await session.commit()
        logger.info("Table Families is updated")

    async def _sync_schedules(self, session):
        result = await session.execute(select(Family))
        families = result.scalars().all()

        for family_obj in families:
            class_num = family_obj.class_num
            schedule_rows = await asyncio.to_thread(
                lambda: self.get_schedule_by_class(class_num)
            )

            for row in schedule_rows:
                date = row.get("date")
                if not date:
                    continue

                data_dict = {
                    "date": date,
                    "child_id": family_obj.id,
                    "class_num": class_num,
                    "text": row.get("text"),
                    "telegram_id": row.get("telegram_id"),
                    "telegram_id2": row.get("telegram_id2"),
                }
                schedule_obj = ScheduleCreate.model_validate(
                    data_dict, from_attributes=True
                )

                result = await session.execute(
                    select(Schedule).where(
                        Schedule.child_id == family_obj.id, Schedule.date == date
                    )
                )
                db_schedule = result.scalars().first()

                if db_schedule:
                    for key, value in schedule_obj.model_dump().items():
                        setattr(db_schedule, key, value)
                else:
                    session.add(Schedule(**schedule_obj.model_dump()))

        await session.commit()
        logger.info("Table Schedules is updated")

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
