from typing import Optional
from pydantic import BaseModel


class ScheduleBase(BaseModel):
    date: str  # формат "dd-mm-YYYY"
    child: Optional[str] = None  # используем id Family для связи
    class_num: int
    mother: Optional[str] = None
    father: Optional[str] = None


class ScheduleCreate(ScheduleBase): ...


class ScheduleRead(ScheduleBase):
    id: int

