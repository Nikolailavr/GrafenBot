from datetime import datetime, timedelta

import gspread

from core.config import BASE_DIR

CREDS = BASE_DIR / "creds.json"
date_format = "%d-%m-%Y"


class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    def get_user_classes(self, telegram_username: str) -> list[str]:
        """
        Ищем пользователя по username или username2 на листе Family.
        Возвращаем список классов (может быть несколько).
        """
        ws_config = self.sh.worksheet("Family")
        data = ws_config.get_all_records()

        user_rows = [
            row
            for row in data
            if row.get("username") == telegram_username
            or row.get("username2") == telegram_username
        ]

        classes = [str(row.get("class")) for row in user_rows if row.get("class")]

        return classes

    def get_user_schedule(self, class_num: str, username: str) -> list[dict]:
        """
        Возвращает список занятий только для указанного пользователя в классе
        """
        schedule = self.get_schedule_by_class(class_num)
        if not schedule:
            return []

        return [
            row
            for row in schedule
            if username
            and (
                username in (row.get("telegram_id"))
                or username in (row.get("telegram_id2"))
            )
        ]

    def get_schedule_by_class(self, class_num: str) -> list[dict]:
        """
        Загружаем расписание из листа Class_[class_num]
        Возвращаем список словарей [{date: ..., text: ...}, ...]
        """
        try:
            ws_class = self.sh.worksheet(f"Class_{class_num}")
        except gspread.exceptions.WorksheetNotFound:
            return []

        return ws_class.get_all_records()

    def get_for_days(self, class_num: str, count_days: int = 5) -> dict:
        """
        Возвращает расписание на count_days вперед начиная с сегодняшнего дня.
        class_schedule — это результат get_schedule_by_class(class_num)
        """
        result = {}
        today = datetime.now().strftime(date_format)
        date = today

        class_schedule = self.get_schedule_by_class(class_num)

        # находим максимальную дату в расписании
        all_dates = [
            datetime.strptime(row["date"], date_format)
            for row in class_schedule
            if row.get("date")
        ]
        max_date = max(all_dates) if all_dates else datetime.now()

        while count_days > 0:
            # ищем по текущей дате
            temp = next(
                (row for row in class_schedule if row.get("date") == date), None
            )
            if temp and temp.get("text"):
                result[date] = temp
                count_days -= 1

            # переходим на следующий день
            date = datetime.strptime(date, date_format) + timedelta(days=1)
            if date > max_date:
                break
            date = date.strftime(date_format)

        return result

    @staticmethod
    def format_schedule(schedule: list[dict], header: str) -> str:
        """Форматирует расписание в удобный текст"""
        if not schedule:
            return header + "\nНет записей"
        mess = header
        for row in schedule:
            mess += f'\n{row["date"]} - {row["text"]}'
        return mess
