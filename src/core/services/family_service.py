from typing import Optional, List

from core.database.db_helper import db_helper
from core.database.schemas import FamilyCreate, FamilyRead

from core.database.DAL.family_CRUD import FamilyCRUD


class FamilyService:
    """Сервис для работы с Family через CRUD"""

    @staticmethod
    async def create_family(family: FamilyCreate) -> FamilyRead:
        async with db_helper.get_session() as session:
            crud = FamilyCRUD(session)
            return await crud.create(family)

    @staticmethod
    async def get_family(
        child: Optional[str] = None, family_id: Optional[int] = None
    ) -> Optional[FamilyRead]:
        async with db_helper.get_session() as session:
            crud = FamilyCRUD(session)
            return await crud.get(child=child, family_id=family_id)

    @staticmethod
    async def update_family(
        child: str, family_in: FamilyCreate
    ) -> Optional[FamilyRead]:
        async with db_helper.get_session() as session:
            crud = FamilyCRUD(session)
            return await crud.update(child, family_in)

    @staticmethod
    async def delete_family(child: str) -> bool:
        async with db_helper.get_session() as session:
            crud = FamilyCRUD(session)
            return await crud.delete(child)

    @staticmethod
    async def list_families(class_num: Optional[int] = None) -> List[FamilyRead]:
        async with db_helper.get_session() as session:
            crud = FamilyCRUD(session)
            return await crud.list(class_num=class_num)
