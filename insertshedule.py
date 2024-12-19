from sqlite3 import IntegrityError
import aiosqlite
import json
from aiogram.fsm.context import FSMContext
import datetime
import asyncio


DB_PATH = 'databaseforschool.db'


async def insert_schedule():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.cursor() as cur:
            schedule_data = [('8В', '8V', json.dumps({
                'pon': [
                    {"number": 1, "time": "12:00 - 12:45", "subject": "Разговор о важном"},
                    {"number": 2, "time": "12:55 - 13:40", "subject": "Физика"},
                    {"number": 3, "time": "13:50 - 14:35", "subject": "География"},
                    {"number": 4, "time": "14:45 - 15:30", "subject": "Математика"},
                    {"number": 5, "time": "15:35 - 16:20", "subject": "Рус-яз"},
                    {"number": 6, "time": "16:25 - 17:10", "subject": "ИЗО/Музыка"},
                    {"number": 7, "time": "17:15 - 18:00", "subject": "Лит-ра"}],

                'vtor': [
                    {"number": 1, "time": "12:00 - 12:45", "subject": "Математика"},
                    {"number": 2, "time": "12:55 - 13:40", "subject": "Химия"},
                    {"number": 3, "time": "13:50 - 14:35", "subject": "История"},
                    {"number": 4, "time": "14:45 - 15:30", "subject": "Род-яз"},
                    {"number": 5, "time": "15:35 - 16:20", "subject": "Ан-яз/Инф-ка"},
                    {"number": 6, "time": "16:25 - 17:10", "subject": "Физ-ра"},
                    {"number": 7, "time": "17:15 - 18:00", "subject": "Ан-яз/Инф-ка"}],

                'sred': [
                    {"number": 1, "time": "12:00 - 12:45", "subject": "ОБЗР"},
                    {"number": 2, "time": "12:55 - 13:40", "subject": "Рус-яз"},
                    {"number": 3, "time": "13:50 - 14:35", "subject": "Ан-яз"},
                    {"number": 4, "time": "14:45 - 15:30", "subject": "Математика"},
                    {"number": 5, "time": "15:35 - 16:20", "subject": "Труд"},
                    {"number": 6, "time": "16:25 - 17:10", "subject": "Биология"},
                    {"number": 7, "time": "17:15 - 18:00", "subject": "Физика"}],

                'chet': [
                    {"number": 0, "time": "11:05 - 11:50", "subject": "Россия-мои горизонты"},
                    {"number": 1, "time": "12:00 - 12:45", "subject": "Химия"},
                    {"number": 2, "time": "12:55 - 13:40", "subject": "Лит-ра"},
                    {"number": 3, "time": "13:50 - 14:35", "subject": "География"},
                    {"number": 4, "time": "14:45 - 15:30", "subject": "История"},
                    {"number": 5, "time": "15:35 - 16:20", "subject": "Математика"},
                    {"number": 6, "time": "16:25 - 17:10", "subject": "Общество"},
                    {"number": 7, "time": "17:15 - 18:00", "subject": "Ан-яз"}],

                'pyat': [
                    {"number": 1, "time": "12:00 - 12:45", "subject": "Биология"},
                    {"number": 2, "time": "12:55 - 13:40", "subject": "Рус-яз"},
                    {"number": 3, "time": "13:50 - 14:35", "subject": "Баш-яз"},
                    {"number": 4, "time": "14:45 - 15:30", "subject": "Математика"},
                    {"number": 5, "time": "15:35 - 16:20", "subject": "Род-лит"},
                    {"number": 6, "time": "16:25 - 17:10", "subject": "ОДНК/Физ-ра"}]}))]

            await db.execute('INSERT INTO school_schedule (cls_rus, class, lessons) VALUES (?, ?, ?)', schedule_data[0])

            await db.commit()


asyncio.run(insert_schedule())

