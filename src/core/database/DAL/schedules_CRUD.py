from datetime import datetime
from typing import Optional, List, Sequence
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
    ) -> Optional[Schedule]:
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
        return schedule

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
            self, child: Optional[str] = None, class_num: Optional[int] = None
    ) -> Sequence[Schedule]:
        from datetime import date

        # Получаем сегодняшнюю дату
        today = date.today().isoformat()  # "YYYY-MM-DD"

        query = select(Schedule).where(Schedule.date >= today)

        if child is not None:
            query = query.where(Schedule.child == child)

        if class_num is not None:
            query = query.where(Schedule.class_num == class_num)

        # Добавляем сортировку по дате в запросе
        query = query.order_by(Schedule.date)

        result = await self.session.execute(query)
        return result.scalars().all()



    async def delete_all(self) -> None:
        try:
            await self.session.execute(delete(Schedule))
            await self.session.commit()
        except Exception:
            ...
