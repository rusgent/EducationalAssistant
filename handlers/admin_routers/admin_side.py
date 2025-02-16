from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import os
from aiogram.fsm.context import FSMContext
from database.orm import Database
from keyboards import inline_kb

from aiogram.filters import BaseFilter
from dotenv import load_dotenv
from aiogram.types import Message
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

admin_ids = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",")]

class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        is_admin = message.from_user.id in self.admin_ids
        return is_admin

admin_ids = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",")]

admin_router = Router()
admin_router.message.filter(IsAdmin(admin_ids))

async def add_proxy_data(state: FSMContext, data: dict):
    # Получите текущее состояние данных
    proxy_data = await state.get_data()

    # Обновите данные
    proxy_data.update(data)
    
    # Установите обновленные данные
    await state.set_data(proxy_data)


@admin_router.message(Command("ad"))
async def cmd_admin_panel(message: Message):
    """Панель администратора для доступа к функциям управления"""
    ADMIN_PANEL_TEXT = (
        "🔐 <b>Админ-панель</b> 🔐\n\n"
        "Выберите одну из доступных команд:\n\n"
        "📋 <b>/view_users</b> — Просмотреть всех пользователей\n"
    )
    await message.answer(ADMIN_PANEL_TEXT, parse_mode="HTML")


@admin_router.message(Command("view_users"))
async def view_users(message: Message):
    """Просмотр списка всех пользователей в базе данных"""
    users = await Database.get_all_users()
    user_count = len(users)

    if users:
        user_list = "\n".join([f"ID: {user.user_id}, Username: @{user.username}, Имя: {user.fullname}" for user in users])

        # Проверка длины сообщения и разбиение, если превышает лимит
        max_message_length = 4000
        if len(user_list) > max_message_length:
            # Разбиваем список на части
            chunks = [user_list[i:i + max_message_length] for i in range(0, len(user_list), max_message_length)]
            for chunk in chunks:
                await message.answer(
                    f"📋 <b>Список пользователей:</b>\n\n{chunk}\n\n"
                    f"🔢 <b>Всего зарегистрировано пользователей:</b> {user_count}",
                    parse_mode="HTML"
                )
        else:
            # Если сообщение помещается в один раз, отправляем его целиком
            await message.answer(
                f"📋 <b>Список пользователей:</b>\n\n{user_list}\n\n"
                f"🔢 <b>Всего зарегистрировано пользователей:</b> {user_count}",
                parse_mode="HTML"
            )
    else:
        await message.answer("❗ Пользователи не найдены в базе данных.")
        
