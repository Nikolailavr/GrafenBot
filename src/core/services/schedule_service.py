import datetime
from typing import Optional, List

from sqlalchemy import select

from core.database.DAL.schedules_CRUD import ScheduleCRUD
from core.database.db_helper import db_helper
from core.database.models import (
    Schedule,
    Family,
)
from core.database.schemas import (
    ScheduleCreate,
    ScheduleRead,
    ScheduleWithFamily,
)


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
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime(
            "%d-%m-%Y"
        )

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
    async def get_week(username: str, days: int = 5) -> list[ScheduleWithFamily]:
        today = datetime.date.today().strftime("%d-%m-%Y")

        async with db_helper.get_session() as session:
            # достаём даты
            result = await session.execute(
                select(Schedule.date)
                .join(Family, Schedule.child_id == Family.id)
                .where(
                    ((Family.mother == username) | (Family.father == username))
                    & (Schedule.date >= today)
                )
                .group_by(Schedule.date)
                .order_by(Schedule.date)
            )
            all_dates = [row[0] for row in result.fetchall()]
            selected_dates = all_dates[:days]
            if not selected_dates:
                return []

            # достаём все записи вместе с Family
            result = await session.execute(
                select(Schedule, Family)
                .join(Family, Schedule.child_id == Family.id)
                .where(
                    ((Family.mother == username) | (Family.father == username))
                    & (Schedule.date.in_(selected_dates))
                )
                .order_by(Schedule.date)
            )

            rows = result.all()

            # собираем схемы
            schedules = [
                ScheduleWithFamily(
                    id=s.id,
                    date=s.date,
                    child=f.child,
                    class_num=f.class_num,
                    mother=f.mother,
                    father=f.father,
                )
                for s, f in rows
            ]
            return schedules
