import asyncio
from apps.sender.google_client import GoogleClient
from sqlalchemy import select

from core.database.db import async_session_maker
from core.database.models.models import Class, User, Schedule

gclient = GoogleClient()


async def sync_google_to_db():
    """
    Синхронизирует Google Sheets с базой данных.
    - Берет лист Family → users и классы
    - Берет листы Class_X → расписание
    """
    async with async_session_maker() as session:
        # 1. Синк классов и пользователей
        family_data = gclient.sh.worksheet("Family").get_all_records()
        for row in family_data:
            class_name = str(row.get("class")).strip()
            if not class_name:
                continue

            # проверяем есть ли класс
            result = await session.execute(
                select(Class).where(Class.name == class_name)
            )
            class_obj = result.scalars().first()
            if not class_obj:
                class_obj = Class(name=class_name)
                session.add(class_obj)
                await session.flush()  # чтобы получить id

            # пользователь
            result = await session.execute(
                select(User).where(User.username == row.get("username"))
            )
            user_obj = result.scalars().first()
            if not user_obj:
                user_obj = User(
                    username=row.get("username"),
                    username2=row.get("username2"),
                    class_id=class_obj.id,
                )
                session.add(user_obj)
            else:
                # обновляем существующего
                user_obj.username2 = row.get("username2")
                user_obj.class_id = class_obj.id

        await session.commit()

        # 2. Синк расписания
        result = await session.execute(select(Class))
        classes = result.scalars().all()

        for class_obj in classes:
            schedule_rows = gclient.get_schedule_by_class(class_obj.name)
            for row in schedule_rows:
                date = row.get("date")
                if not date:
                    continue
                # проверяем есть ли запись
                result = await session.execute(
                    select(Schedule).where(
                        Schedule.class_id == class_obj.id, Schedule.date == date
                    )
                )
                sched_obj = result.scalars().first()
                if not sched_obj:
                    sched_obj = Schedule(
                        class_id=class_obj.id,
                        date=date,
                        text=row.get("text"),
                        telegram_id=row.get("telegram_id"),
                        telegram_id2=row.get("telegram_id2"),
                    )
                    session.add(sched_obj)
                else:
                    sched_obj.text = row.get("text")
                    sched_obj.telegram_id = row.get("telegram_id")
                    sched_obj.telegram_id2 = row.get("telegram_id2")

        await session.commit()


# Тестовый запуск
if __name__ == "__main__":
    asyncio.run(sync_google_to_db())
