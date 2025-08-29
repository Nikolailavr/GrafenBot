import datetime
from typing import Optional, List

from sqlalchemy import select

from core.database.DAL.schedules_CRUD import ScheduleCRUD
from core.database.db_helper import db_helper
from core.database.models import Schedule, Family
from core.database.schemas import ScheduleCreate, ScheduleRead


class ScheduleService:
    """Сервис для работы с Schedule через CRUD"""

    @staticmethod
    async def create_schedule(schedule_in: ScheduleCreate) -> ScheduleRead:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.create(schedule_in)

    @staticmethod
    async def get_schedule(schedule_id: int) -> Optional[ScheduleRead]:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.get(schedule_id)

    @staticmethod
    async def update_schedule(
        schedule_id: int, schedule_in: ScheduleCreate
    ) -> Optional[ScheduleRead]:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.update(schedule_id, schedule_in)

    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.delete(schedule_id)

    @staticmethod
    async def list_schedules(
        child_id: Optional[int] = None, class_num: Optional[int] = None
    ) -> List[ScheduleRead]:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.list(child_id=child_id, class_num=class_num)

    @staticmethod
    async def get_by_parents(username: str) -> list[Schedule]:
        """Найти расписание по username родителей"""
        async with db_helper.get_session() as session:
            result = await session.execute(
                select(Schedule)
                .join(Family, Schedule.child_id == Family.id)
                .where((Family.mother == username) | (Family.father == username))
                .order_by(Schedule.date)
            )
            return result.scalars().all()

    @staticmethod
    async def get_tomorrow(username: str) -> list[Schedule]:
        """Расписание на завтра"""
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")

        async with db_helper.get_session() as session:
            result = await session.execute(
                select(Schedule)
                .join(Family, Schedule.child_id == Family.id)
                .where(
                    ((Family.mother == username) | (Family.father == username))
                    & (Schedule.date == tomorrow)
                )
                .order_by(Schedule.date)
            )
            return result.scalars().all()

    @staticmethod
    async def get_week(username: str, days: int = 5) -> list[Schedule]:
        """Расписание на неделю (берём ближайшие N дней из БД)"""
        today = datetime.date.today().strftime("%d-%m-%Y")

        async with db_helper.get_session() as session:
            result = await session.execute(
                select(Schedule)
                .join(Family, Schedule.child_id == Family.id)
                .where(
                    (Family.mother == username) | (Family.father == username)
                )
                .order_by(Schedule.date)
            )
            all_records = result.scalars().all()

            # фильтруем только >= сегодня
            upcoming = [s for s in all_records if s.date >= today]

            # берём уникальные даты
            seen_dates = set()
            limited = []
            for s in upcoming:
                if s.date not in seen_dates:
                    seen_dates.add(s.date)
                if len(seen_dates) > days:
                    break
                limited.append(s)

            return limited
