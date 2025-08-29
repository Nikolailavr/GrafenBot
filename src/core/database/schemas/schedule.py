from typing import Optional
from pydantic import BaseModel


class ScheduleBase(BaseModel):
    date: str  # формат "dd-mm-YYYY"
    child_id: Optional[int] = None  # используем id Family для связи


class ScheduleCreate(ScheduleBase): ...


class ScheduleRead(ScheduleBase):
    id: int


class ScheduleWithFamily(BaseModel):
    id: int
    date: str
    child: str
    class_num: int
    mother: Optional[str] = None
    father: Optional[str] = None
