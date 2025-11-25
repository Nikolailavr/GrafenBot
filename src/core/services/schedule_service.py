from datetime import datetime, timedelta
from typing import Optional, List, Dict

from core.database.DAL.schedules_CRUD import ScheduleCRUD
from core.database.db_helper import db_helper
from core.database.schemas import ScheduleCreate, ScheduleRead
from core.services import FamilyService

DATE_FORMAT = "%Y-%m-%d"


class ScheduleService:
    """Сервис для работы с Schedule через CRUD"""

    # ======================================================
    # Вспомогательные методы
    # ======================================================
    @staticmethod
    async def _get_families() -> list:
        """Возвращает список всех семей"""
        return await FamilyService.list_families()

    @staticmethod
    def _filter_families_by_user(families: list, username: str) -> list:
        return [f for f in families if username in (f.mother, f.father)]

    @staticmethod
    def _find_family_for_child(families: list, child_id: str):
        return next((f for f in families if f.child == child_id), None)

    @staticmethod
    def _build_schedule_read(schedule, family) -> ScheduleRead:
        return ScheduleRead(
            id=schedule.id,
            date=schedule.date,
            child=family.child,
            class_num=family.class_num,
            mother=family.mother,
            father=family.father,
        )

    # ======================================================
    # CRUD
    # ======================================================

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
    async def update_schedule(schedule_id: int, schedule_in: ScheduleCreate) -> Optional[ScheduleRead]:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.update(schedule_id, schedule_in)

    @staticmethod
    async def delete_schedule(schedule_id: int) -> bool:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            return await crud.delete(schedule_id)

    @staticmethod
    async def list_schedules(child: Optional[str] = None, class_num: Optional[int] = None) -> List[ScheduleRead]:
        async with db_helper.get_session() as session:
            crud = ScheduleCRUD(session)
            schedules = await crud.list(child=child, class_num=class_num)
            return [ScheduleRead.model_validate(s, from_attributes=True) for s in schedules]

    @staticmethod
    async def delete_table() -> None:
        async with db_helper.get_session() as session:
            await ScheduleCRUD(session).delete_all()

    # ======================================================
    # Расширенные методы
    # ======================================================

    @staticmethod
    async def get_by_parents(username: str) -> dict[int, List[ScheduleRead]]:
        """Все расписания по username родителей, сгруппированные по class_num"""
        families = await ScheduleService._get_families()
        user_families = ScheduleService._filter_families_by_user(families, username)
        if not user_families:
            return {}

        class_nums = {f.class_num for f in user_families}
        result: dict[int, List[ScheduleRead]] = {}

        for class_num in class_nums:
            class_schedules = await ScheduleService.list_schedules(class_num=class_num)
            for s in class_schedules:
                family = ScheduleService._find_family_for_child(user_families, s.child)
                if family:
                    result.setdefault(class_num, []).append(
                        ScheduleService._build_schedule_read(s, family)
                    )

        return result

    @staticmethod
    async def get_tomorrow(class_num: int) -> Optional[ScheduleRead]:
        """Расписание на завтра"""
        tomorrow = (datetime.today() + timedelta(days=1)).strftime(DATE_FORMAT)
        families = await ScheduleService._get_families()
        class_schedules = await ScheduleService.list_schedules(class_num=class_num)

        for s in class_schedules:
            if s.date == tomorrow:
                family = ScheduleService._find_family_for_child(families, s.child)
                if family:
                    return ScheduleService._build_schedule_read(s, family)

        return None

    @staticmethod
    async def get_class_parents(username: str) -> List[int]:
        families = await ScheduleService._get_families()
        user_families = ScheduleService._filter_families_by_user(families, username)
        return list({f.class_num for f in user_families}) if user_families else []

    @staticmethod
    async def get_week(class_num: int, days: int = 5) -> Optional[Dict[int, List[ScheduleRead]]]:
        families = await ScheduleService._get_families()
        class_schedules = await ScheduleService.list_schedules(class_num=class_num)
        today_str = datetime.today().strftime(DATE_FORMAT)

        start_index = next((i for i, s in enumerate(class_schedules) if s.date >= today_str), None)
        if start_index is None:
            return None

        schedules_slice = class_schedules[start_index:start_index + days]
        result: Dict[int, List[ScheduleRead]] = {}

        for s in schedules_slice:
            family = ScheduleService._find_family_for_child(families, s.child)
            if family:
                result.setdefault(class_num, []).append(
                    ScheduleService._build_schedule_read(s, family)
                )

        return result
