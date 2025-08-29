from sqlalchemy import Integer, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import Base


class Class(Base):
    num: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    families: Mapped[list["Family"]] = relationship(back_populates="class_")
