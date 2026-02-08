from typing import Optional, List

from sqlalchemy import delete

from core.database.DAL.classes_CRUD import ClassCRUD
from core.database.db_helper import db_helper
from core.database.schemas import ClassCreate, ClassRead


class ClassService:
    """Сервис для работы с Class через CRUD"""

    @staticmethod
    async def create_class(class_in: ClassCreate) -> ClassRead:
        async with db_helper.get_session() as session:
            class_ = await ClassCRUD(session).create(class_in)
            return ClassRead.model_validate(class_, from_attributes=True)

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
            classes = await ClassCRUD(session).list()
            return [ClassRead.model_validate(c, from_attributes=True) for c in classes]

    @staticmethod
    async def delete_table() -> None:
        async with db_helper.get_session() as session:
            await ClassCRUD(session).delete_all()
