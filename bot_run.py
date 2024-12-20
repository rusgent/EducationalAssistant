import asyncio
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from handlers.user_routers import user_router
from handlers.admin_routers import admin_router
from dotenv import load_dotenv
import os
from aiogram.client.default import DefaultBotProperties
from database.orm import Database


load_dotenv()
storage = MemoryStorage()


async def on_startup(bot):
    await Database.db_start()
    print('Bot Online!')
    await bot.send_message(chat_id=os.getenv("RUS_ID"), text='Бот запущен!')


async def stop_bot(bot):
    await bot.send_message(chat_id=os.getenv("RUS_ID"), text='Бот выключен!')


async def main():
    bot = Bot(token=os.getenv('TOKEN'),
              default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=storage)

    dp.startup.register(on_startup)
    dp.shutdown.register(stop_bot)
    
    await bot.delete_webhook(True)
    dp.include_routers(user_router, admin_router)
    await dp.start_polling(bot)
    
if __name__ == '__main__':
    asyncio.run(main())