import asyncio
import datetime
import logging

from core import settings
from core.database.schemas import ClassCreate, FamilyCreate, ScheduleCreate

import gspread

from core.config import BASE_DIR, bot
from core.services import ClassService, FamilyService, ScheduleService

CREDS = BASE_DIR / "creds.json"
date_format = "%d-%m-%Y"
logger = logging.getLogger(__name__)


class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    async def sync_google_to_db(self):
        try:
            await self._sync_classes()
            await self._sync_families()
            await self._sync_schedules()
        except Exception as ex:
            logger.exception("Критическая ошибка при синхронизации таблицы")
            await bot.send_message(
                chat_id=settings.telegram.admin_chat_id,
                text=f"Критическая ошибка при синхронизации таблицы:\n{ex}",
            )

    async def _sync_classes(self):
        await ClassService.delete_table()

        classes_data = await asyncio.to_thread(
            lambda: self.sh.worksheet("Config").get_all_records()
        )

        for row in classes_data:
            class_raw = row.get("class")

            # Проверяем, что класс указан и является числом
            if class_raw == "" or class_raw is None:
                logger.warning(f"Пропущена строка в Config, нет номера класса: {row}")
                continue

            try:
                class_num = int(class_raw)
            except ValueError:
                logger.warning(f"Пропущена строка в Config, неверный формат класса: {class_raw}")
                continue

            class_in = ClassCreate(
                num=class_num,
                chat_id=row.get("chat_id") or None  # Заменяем "" на None, если пусто
            )
            await ClassService.create_class(class_in)

        logger.info("Classes synced")

    async def _sync_families(self):
        await FamilyService.delete_table()

        family_data = await asyncio.to_thread(
            lambda: self.sh.worksheet("Family").get_all_records()
        )

        for row in family_data:
            class_raw = row.get("class")

            # Проверяем наличие класса
            if class_raw == "" or class_raw is None:
                logger.warning(f"Пропущена семья, не указан класс: {row}")
                continue

            try:
                class_num = int(class_raw)
            except ValueError:
                logger.warning(f"Пропущена семья, неверный формат класса: {class_raw}")
                continue

            # Проверяем, что такой класс есть в базе
            existing_class = await ClassService.get_class(class_num)
            if not existing_class:
                logger.warning(f"Семья пропущена, класс {class_num} не найден в БД")
                continue

            # Проверяем, что указан ребенок/семья (если это обязательное поле)
            child_name = row.get("family")
            if not child_name:
                logger.warning(f"Пропущена строка, не указано имя (family): {row}")
                continue

            family_in = FamilyCreate(
                child=child_name,
                mother=str(row.get("username") or ""),
                father=str(row.get("username2") or ""),
                class_num=class_num,
            )

            await FamilyService.create_family(family_in)

        logger.info("Families synced")

    async def _sync_schedules(self):
        await ScheduleService.delete_table()
        classes = await ClassService.list_classes()
        class_nums = {class_obj.num for class_obj in classes}

        # Список для накопления всех объектов перед сохранением
        schedules_to_create = []

        for num in class_nums:
            schedule_rows = await asyncio.to_thread(
                lambda: self.get_schedule_by_class(num)
            )
            for row in schedule_rows:
                date_str = row.get("date")

                # Если дата пустая — пропускаем
                if not date_str:
                    continue

                try:
                    date_dt = datetime.datetime.strptime(str(date_str).strip(), date_format)
                    formatted_date = date_dt.strftime("%Y-%m-%d")

                    child = row.get("text")
                    if not child:
                        # Если нет текста (ребенка), нет смысла создавать запись
                        continue

                    schedule_in = ScheduleCreate(
                        date=formatted_date,
                        child=child,
                        class_num=num,
                        mother=row.get("telegram_id") or None,
                        father=row.get("telegram_id2") or None,
                    )
                    # Добавляем в список
                    schedules_to_create.append(schedule_in)

                except ValueError:
                    # Отлавливаем именно ошибку парсинга даты, чтобы не ломать весь скрипт
                    logger.error("Bad date format for %s, date: %s", row.get("text"), date_str)
                    await bot.send_message(
                        chat_id=settings.telegram.admin_chat_id,
                        text=f"Неверный формат даты!\nТекст: {row.get('text')}\nДата: {date_str}\nКласс: {num}"
                    )
                except Exception as ex:
                    logger.error("Error processing row: %s. Error: %s", row, ex)

        # ВАЖНО: сохраняем всё одним махом
        if schedules_to_create:
            await ScheduleService.create_schedules_bulk(schedules_to_create)

        logger.info(f"Schedules synced. Total records: {len(schedules_to_create)}")

    def get_schedule_by_class(self, class_num: int) -> list[dict]:
        try:
            ws_class = self.sh.worksheet(f"Class_{class_num}")
        except gspread.exceptions.WorksheetNotFound:
            return []

        # Если expected_headers не совпадает с реальными, gspread тоже может ругаться.
        # Если структура жесткая, оставляем как есть.
        return ws_class.get_all_records(expected_headers=["id_", "date", "text", "telegram_id", "telegram_id2"])


# -----------------------
# Тестовый запуск
# -----------------------
if __name__ == "__main__":
    asyncio.run(GoogleClient().sync_google_to_db())