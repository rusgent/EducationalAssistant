from sqlalchemy import JSON, DateTime, String, Text, Enum, func, BigInteger, VARCHAR
from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import declarative_base

intpk = Annotated[int, mapped_column(primary_key=True)]
Base = declarative_base()

class Users(Base):

    __tablename__ = 'users'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(BigInteger,nullable=False)
    username: Mapped[str]
    fullname: Mapped[str]
    favcls: Mapped[dict] = mapped_column(JSON)


class Results(Base):

    __tablename__ = 'results'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(BigInteger,nullable=False)
    result: Mapped[str]
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=func.now())


class SchoolShedule(Base):
    __tablename__ = 'school_schedule'

    id: Mapped[intpk]
    cls_eng: Mapped[str]
    lessons: Mapped[dict] = mapped_column(JSON)
    cls_rus: Mapped[str]


class Tasks(Base):
    __tablename__ = 'tasks'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    task_name: Mapped[str]
    description: Mapped[str]
    status: Mapped[str] = mapped_column(Enum('🔴 Не выполнено', '🟢 Выполнено', name='task_status'), default='🔴 Не выполнено')