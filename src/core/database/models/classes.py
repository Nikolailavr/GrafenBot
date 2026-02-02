from sqlalchemy import Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models import Base


class Class(Base):
    __tablename__ = "classes"


    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    num: Mapped[int] = mapped_column(Integer, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    families: Mapped[list["Family"]] = relationship(back_populates="class_")
