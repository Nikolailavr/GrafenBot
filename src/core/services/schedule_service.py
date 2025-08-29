from datetime import datetime, timedelta
from multiprocessing.connection import families
from typing import Optional, List, Dict

from aiogram.types import Message
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
    async def get_by_parents(username: str) -> dict[int, list[ScheduleWithFamily]]:
        """Найти все расписания по username родителей, сгруппированные по class_num"""
        families = await FamilyService.list_families()

        # 1. Получаем семьи пользователя
        user_families = [f for f in families if username in (f.mother, f.father)]
        if not user_families:
            return {}

        # 2. Собираем классы
        class_nums = list({f.class_num for f in user_families})
        schedules: dict[int, list[ScheduleWithFamily]] = {}

        # 3. Ищем расписания для всех классов
        for class_num in class_nums:
            class_schedules = await ScheduleService.list_schedules(class_num=class_num)
            for s in class_schedules:
                # находим ребёнка для записи
                child = next((f for f in user_families if f.id == s.child_id), None)
                if child:
                    schedules.setdefault(class_num, []).append(
                        ScheduleWithFamily(
                            id=s.id,
                            date=s.date,
                            child=child.child,
                            class_num=child.class_num,
                            mother=child.mother,
                            father=child.father,
                        )
                    )
        return schedules

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
    async def get_week(days: int = 5) -> Dict[int, List[ScheduleWithFamily]] | None:
        families = await FamilyService.list_families()
        if not families:
            return None

        class_nums = list({f.class_num for f in families})
        today_str = datetime.today().strftime(date_format)

        schedules: dict[int, list[ScheduleWithFamily]] = dict()
        for class_num in class_nums:
            class_schedules = await ScheduleService.list_schedules(class_num=class_num)
            # находим индекс первой записи с сегодняшней датой
            start_index = next(
                (i for i, s in enumerate(class_schedules) if s.date >= today_str), None
            )
            if start_index is None:
                continue  # нет записей сегодня и позже

            # берём срез ближайших N дней
            for s in class_schedules[start_index : start_index + days]:
                child = next((f for f in families if f.id == s.child_id), None)
                if child:
                    schedules.setdefault(class_num, []).append(
                        ScheduleWithFamily(
                            id=s.id,
                            date=s.date,
                            child=child.child,
                            class_num=child.class_num,
                            mother=child.mother,
                            father=child.father,
                        )
                    )
        return schedules
