# from datetime import datetime, timedelta
#
#
# date_format = '%d-%m-%Y'
#
#
# class SenderData:
#     @classmethod
#     async def get_all_schedule(cls) -> dict:
#         return cls.__get_data_from_sheet()
#
#     @classmethod
#     async def get_by_child(cls, telegram_id: str) -> dict:
#         sheet = cls.__get_data_from_sheet()
#         result = {}
#         for date, values in sheet.items():
#             if temp := sheet.get(date):
#                 if (telegram_id == temp.get('telegram_id', None) or
#                         telegram_id == temp.get('telegram_id2', None)):
#                     result[date] = temp
#         return result
#
#     @classmethod
#     def __get_data_from_sheet(cls) -> dict:
#         sheet = GoogleSheet.get_file('GrafenDaily')
#         result = {}
#         for num, row in enumerate(sheet):
#             if num > 0 and row[0] != '':
#                 result[row[1]] = {
#                     'date': row[1],
#                     'text': row[2],
#                     'telegram_id': row[3],
#                     'telegram_id2': row[4],
#                     'event': row[5],
#                     'name': row[6],
#                 }
#         return result
#
#     @classmethod
#     async def get_for_days(cls, count_days: int = 5) -> dict:
#         date = datetime.now().strftime(date_format)
#         sheet = cls.__get_data_from_sheet()
#         result = {}
#         while count_days > 0:
#             if temp := sheet.get(date):
#                 if temp.get("text", None):
#                     result[date] = temp
#                     count_days -= 1
#             date = datetime.strptime(date, date_format) + timedelta(days=1)
#             if date > datetime.strptime("31-05-2025", date_format):
#                 break
#             date = date.strftime(date_format)
#         return result
