from datetime import datetime, timedelta

from apps.sender.misc.sheet import GoogleSheet

date_format = '%d-%m-%Y'


class SenderData:
    @classmethod
    async def get_data_by_days(cls, date: str = None, count_days: int = 1) -> dict:
        if date is None:
            date = datetime.now() + timedelta(days=1)
            date = date.strftime(date_format)
        sheet = cls.__get_data_from_sheet()
        return cls.__modify_data(sheet, date, count_days=count_days)

    @classmethod
    async def get_data_by_child(cls, telegram_id: str) -> dict:
        date = datetime.now().strftime(date_format)
        sheet = cls.__get_data_from_sheet()
        result = {}
        for date, values in sheet.items():
            if temp := sheet.get(date):
                if telegram_id == temp.get('telegram_id', None):
                    result[date] = temp
        return result

    @classmethod
    def __get_data_from_sheet(cls):
        sheet = GoogleSheet.get_file('GrafenDaily')
        result = {}
        for num, row in enumerate(sheet):
            if num > 0 and row[1] != '':
                result[row[1]] = {
                    'date': row[1],
                    'text': row[2],
                    'telegram_id': row[3]
                }
        return result

    @staticmethod
    def __modify_data(sheet: dict, date: str, count_days: int = 1):
        result = {}
        while count_days > 0:
            if temp := sheet.get(date):
                result[date] = temp
                count_days -= 1
            date = datetime.strptime(date, date_format) + timedelta(days=1)
            date = date.strftime(date_format)
        return result


