from typing import Optional, List

from core.database.DAL.classes_CRUD import ClassCRUD
from core.database.db_helper import db_helper
from core.database.schemas import ClassCreate, ClassRead


class ClassService:
    """Сервис для работы с Class через CRUD"""

    @staticmethod
    async def create_class(class_in: ClassCreate) -> ClassRead:
        async with db_helper.get_session() as session:
            crud = ClassCRUD(session)
            return await crud.create(class_in)

    @staticmethod
    async def get_class(num: int) -> Optional[ClassRead]:
        async with db_helper.get_session() as session:
            crud = ClassCRUD(session)
            return await crud.get(num)

    @staticmethod
    async def update_class(class_in: ClassCreate) -> Optional[ClassRead]:
        async with db_helper.get_session() as session:
            crud = ClassCRUD(session)
            return await crud.update(class_in)

    @staticmethod
    async def delete_class(num: int) -> bool:
        async with db_helper.get_session() as session:
            crud = ClassCRUD(session)
            return await crud.delete(num)

    @staticmethod
    async def list_classes() -> List[ClassRead]:
        async with db_helper.get_session() as session:
            crud = ClassCRUD(session)
            return await crud.list()
