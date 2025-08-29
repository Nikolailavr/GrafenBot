from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Family
from core.database.schemas import FamilyCreate, FamilyRead


class FamilyCRUD:
    """Асинхронный CRUD для Family с внешней сессией"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, family_in: FamilyCreate) -> FamilyRead:
        family = Family(**family_in.model_dump())
        self.session.add(family)
        await self.session.commit()
        await self.session.refresh(family)
        return FamilyRead.model_validate(family, from_attributes=True)

    async def get(
        self, child: Optional[str] = None, family_id: Optional[int] = None
    ) -> Optional[FamilyRead]:
        query = select(Family)
        if child:
            query = query.where(Family.child == child)
        elif family_id:
            query = query.where(Family.id == family_id)
        else:
            return None

        result = await self.session.execute(query)
        family = result.scalars().first()
        if family:
            return FamilyRead.model_validate(family, from_attributes=True)
        return None

    async def update(self, child: str, family_in: FamilyCreate) -> Optional[FamilyRead]:
        result = await self.session.execute(select(Family).where(Family.child == child))
        family = result.scalars().first()
        if not family:
            return None

        for key, value in family_in.model_dump(exclude_unset=True).items():
            setattr(family, key, value)

        await self.session.commit()
        await self.session.refresh(family)
        return FamilyRead.model_validate(family, from_attributes=True)

    async def delete(self, child: str) -> bool:
        result = await self.session.execute(select(Family).where(Family.child == child))
        family = result.scalars().first()
        if not family:
            return False

        await self.session.delete(family)
        await self.session.commit()
        return True

    async def list(self, class_num: Optional[int] = None) -> List[FamilyRead]:
        query = select(Family)
        if class_num is not None:
            query = query.where(Family.class_num == class_num)

        result = await self.session.execute(query)
        families = result.scalars().all()
        return [FamilyRead.model_validate(f, from_attributes=True) for f in families]

    async def delete_all(self) -> None:
        await self.session.execute(delete(Family))
        await self.session.commit()
