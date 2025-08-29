from datetime import datetime, timedelta
from multiprocessing.connection import families
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
from core.services import FamilyService

date_format = "%Y-%m-%d"


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
        tomorrow = (datetime.today() + timedelta(days=1)).strftime(date_format)

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

        families = await FamilyService.list_families()
        # 1. Получаем всех детей пользователя через FamilyService
        user_families = [
            family for family in families if username in (family.mother, family.father)
        ]
        if not user_families:
            return []

        # 2. Все уникальные классы
        class_nums = list({f.class_num for f in user_families})

        # 3. Список ближайших дней
        today_dt = datetime.today()
        selected_dates = [
            (today_dt + timedelta(days=i)).strftime(date_format)
            for i in range(days * 2)
        ]

        # 4. Сбор всех записей по классам и выбранным датам через ScheduleService
        schedules = []
        for class_num in class_nums:
            class_schedules = await ScheduleService.list_schedules(class_num=class_num)
            for s in class_schedules:
                if s.date in selected_dates:
                    # находим child info
                    child = next((f for f in families if f.id == s.child_id), None)
                    if child:
                        schedules.append(
                            ScheduleWithFamily(
                                id=s.id,
                                date=s.date,
                                child=child.child,
                                class_num=child.class_num,
                                mother=child.mother,
                                father=child.father,
                            )
                        )

        # 5. сортируем по дате
        schedules.sort(key=lambda x: datetime.strptime(x.date, date_format))
        return schedules[:days]
