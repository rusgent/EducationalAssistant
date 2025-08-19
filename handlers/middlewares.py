from typing import Callable, Dict, Any, Awaitable
from handlers.user_routers.common import cmd_start
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from database.orm import Database
import datetime

class CheckMiddleware(BaseMiddleware):
    
    def __init__(self):
        pass
        
    async def __call__(self, handler, event, data):

        if isinstance(event, Message) and event.text == '/start':
            return await handler(event, data)
        user = await Database.check_in_premium_users_table(event.from_user.id)

        if not user:    
            return await event.answer("❌ Ваша подписка неактивна. Пожалуйста, продлите её, чтобы пользоваться ботом.")

        check_premium = await Database.check_premium(event.from_user.id)
        
        if user and check_premium == 2:
            return await handler(event, data)

            
            
            
        
        