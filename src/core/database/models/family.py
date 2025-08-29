from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base


class Family(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    child: Mapped[str] = mapped_column(String, unique=True, index=True)
    mother: Mapped[str] = mapped_column(String, index=True)
    father: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    class_num: Mapped[int] = mapped_column(ForeignKey("class.num"))

    schedules: Mapped[list["Schedule"]] = relationship(back_populates="child")
    class_: Mapped["Class"] = relationship(back_populates="families")
