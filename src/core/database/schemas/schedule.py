from typing import Optional
from pydantic import BaseModel


class ScheduleBase(BaseModel):
    date: str  # формат "dd-mm-YYYY"
    child_id: Optional[int] = None  # используем id Family для связи
    class_num: int
    text: Optional[str] = None
    telegram_id: Optional[str] = None
    telegram_id2: Optional[str] = None


class ScheduleCreate(ScheduleBase): ...


class ScheduleRead(ScheduleBase):
    id: int
