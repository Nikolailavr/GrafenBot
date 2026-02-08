from sqlite3 import OperationalError
from typing import Optional, List, Sequence
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models import Class
from core.database.schemas import ClassCreate, ClassRead


class ClassCRUD:
    """CRUD для Class через переданную сессию"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, class_in: ClassCreate) -> Class:
        class_obj = Class(**class_in.model_dump())
        self.session.add(class_obj)
        await self.session.commit()
        await self.session.refresh(class_obj)
        return class_obj

    async def get(self, num: int) -> Sequence[Class] | None:
        result = await self.session.execute(select(Class).where(Class.num == num))
        class_obj = result.scalars().all()
        if class_obj:
            return class_obj
        return None

    async def update(self, class_in: ClassCreate) -> Optional[ClassRead]:
        result = await self.session.execute(
            select(Class).where(Class.num == class_in.num)
        )
        class_obj = result.scalars().first()
        if not class_obj:
            return None

        for key, value in class_in.model_dump(exclude_unset=True).items():
            setattr(class_obj, key, value)

        await self.session.commit()
        await self.session.refresh(class_obj)
        return ClassRead.model_validate(class_obj, from_attributes=True)

    async def delete(self, num: int) -> bool:
        result = await self.session.execute(select(Class).where(Class.num == num))
        class_obj = result.scalars().first()
        if not class_obj:
            return False

        await self.session.delete(class_obj)
        await self.session.commit()
        return True

    async def list(self) -> Sequence[Class]:
        result = await self.session.execute(select(Class))
        return result.scalars().all()

    async def delete_all(self) -> None:
        try:
            await self.session.execute(delete(Class))
            await self.session.commit()
        except Exception:
            pass
