from typing import Optional, List
from pydantic import BaseModel

from core.database.schemas import ScheduleRead


class FamilyBase(BaseModel):
    child: str
    # Разрешаем полям быть строкой или None (Null)
    mother: Optional[str] = None
    father: Optional[str] = None
    class_num: int


class FamilyCreate(FamilyBase): ...


class FamilyRead(FamilyBase):
    id: int
