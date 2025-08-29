from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.db.db import Base


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="class_")
    schedules = relationship("Schedule", back_populates="class_")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    username2 = Column(String)
    class_id = Column(Integer, ForeignKey("classes.id"))

    class_ = relationship("Class", back_populates="users")


class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    date = Column(String, index=True)  # dd-mm-YYYY
    text = Column(Text)
    telegram_id = Column(String)
    telegram_id2 = Column(String)

    class_ = relationship("Class", back_populates="schedules")
