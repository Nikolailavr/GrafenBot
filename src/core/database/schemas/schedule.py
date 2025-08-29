from typing import Optional
from pydantic import BaseModel


class ScheduleBase(BaseModel):
    date: str  # формат "dd-mm-YYYY"
    child_id: Optional[int] = None  # используем id Family для связи


class ScheduleCreate(ScheduleBase): ...


class ScheduleRead(ScheduleBase):
    id: int
