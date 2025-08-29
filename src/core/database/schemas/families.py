from typing import Optional, List
from pydantic import BaseModel

from core.database.schemas import ScheduleRead


class FamilyBase(BaseModel):
    child: str
    mother: str
    father: Optional[str] = None
    class_num: int


class FamilyCreate(FamilyBase): ...


class FamilyRead(FamilyBase):
    id: int
    schedules: List[ScheduleRead] = []
