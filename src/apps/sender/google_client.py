from datetime import datetime, timedelta

import gspread

from core.config import BASE_DIR

CREDS = BASE_DIR / "creds.json"
date_format = '%d-%m-%Y'

class GoogleClient:
    def __init__(self, sheet_name: str = "GrafenDaily"):
        self.gc = gspread.service_account(filename=CREDS)
        self.sh = self.gc.open(sheet_name)

    def get_user_class(self, telegram_username: str) -> str | None:
        """
        Ищем пользователя по username или username2 на листе config
        Возвращаем значение class или None, если не найден
        """
        ws_config = self.sh.worksheet("Family")
        data = ws_config.get_all_records()

        user_row = next(
            (
                row for row in data
                if row.get("username") == telegram_username
                or row.get("username2") == telegram_username
            ),
            None
        )

        if not user_row:
            return None
        return str(user_row.get("class")) if user_row.get("class") else None

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

        while count_days > 0:
            # ищем по текущей дате
            temp = next((row for row in class_schedule if row.get("date") == date), None)
            if temp and temp.get("text"):
                result[date] = temp
                count_days -= 1

            # переходим на следующий день
            date = datetime.strptime(date, date_format) + timedelta(days=1)
            if date > datetime.strptime("31-05-2025", date_format):
                break
            date = date.strftime(date_format)

        return result
