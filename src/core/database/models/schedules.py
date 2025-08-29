from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base


class Schedule(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String, index=True)  # dd-mm-YYYY
    child_id: Mapped[int] = mapped_column(ForeignKey("family.id"))

    child: Mapped["Family"] = relationship("Family", back_populates="schedules")
