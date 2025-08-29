from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Schedule, Family
from core.database.schemas import ScheduleCreate, ScheduleRead


class ScheduleCRUD:
    """CRUD для Schedule через переданную сессию"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, schedule_in: ScheduleCreate) -> ScheduleRead:
        schedule = Schedule(**schedule_in.model_dump())
        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        return ScheduleRead.model_validate(schedule, from_attributes=True)

    async def get(self, schedule_id: int) -> Optional[ScheduleRead]:
        result = await self.session.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        schedule = result.scalars().first()
        if schedule:
            return ScheduleRead.model_validate(schedule, from_attributes=True)
        return None

    async def update(
        self, schedule_id: int, schedule_in: ScheduleCreate
    ) -> Optional[ScheduleRead]:
        result = await self.session.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        schedule = result.scalars().first()
        if not schedule:
            return None

        for key, value in schedule_in.model_dump(exclude_unset=True).items():
            setattr(schedule, key, value)

        await self.session.commit()
        await self.session.refresh(schedule)
        return ScheduleRead.model_validate(schedule, from_attributes=True)

    async def delete(self, schedule_id: int) -> bool:
        result = await self.session.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        schedule = result.scalars().first()
        if not schedule:
            return False

        await self.session.delete(schedule)
        await self.session.commit()
        return True

    async def list(
        self, child_id: Optional[int] = None, class_num: Optional[int] = None
    ) -> List[ScheduleRead]:
        query = select(Schedule)

        if child_id is not None:
            query = query.where(Schedule.child_id == child_id)

        if class_num is not None:
            query = query.where(Schedule.class_num == class_num)

        result = await self.session.execute(query)
        schedules = result.scalars().all()

        # сортировка по дате
        schedules.sort(key=lambda s: datetime.strptime(s.date, "%Y-%m-%d"))

        return [ScheduleRead.model_validate(s, from_attributes=True) for s in schedules]

    async def delete_all(self) -> None:
        await self.session.execute(delete(Schedule))
        await self.session.commit()
