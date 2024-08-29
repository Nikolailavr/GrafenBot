from datetime import datetime, timedelta

from apps.sender.misc.sheet import GoogleSheet


class SenderData:
    @classmethod
    async def get_data(cls, date: str = None) -> dict:
        if date is None:
            date = datetime.now() + timedelta(days=1)
            date = date.strftime('%Y-%m-%d')
        data = cls.__get_data_from_sheet(date)
        return data

    @staticmethod
    def __get_data_from_sheet(date_now: str):
        sheet = GoogleSheet.get_file('GrafenDaily')
        result = {}
        for num, row in enumerate(sheet):
            if num > 0:
                result[row[1]] = {
                    'text': row[2],
                    'telegram_id': row[3]
                }
        return result.get(date_now, None)
