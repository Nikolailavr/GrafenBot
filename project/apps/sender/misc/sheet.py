import gspread
from django.conf import settings

CREDS = settings.BASE_DIR / "creds.json"


class GoogleSheet:
    service = gspread.service_account(filename=CREDS)

    @classmethod
    def get_file(cls, name: str) -> list | None:
        """Получение данных из файла"""
        return cls.service.open(name).sheet1.get_values()
