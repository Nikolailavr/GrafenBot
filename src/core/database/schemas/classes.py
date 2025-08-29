from typing import Optional, List
from pydantic import BaseModel

from core.database.schemas import FamilyRead


class ClassBase(BaseModel):
    num: int
    chat_id: Optional[int] = None


class ClassCreate(ClassBase): ...


class ClassRead(ClassBase): ...
