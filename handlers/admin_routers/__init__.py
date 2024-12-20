from aiogram.filters import BaseFilter
from dotenv import load_dotenv
from aiogram.types import Message
import os
from aiogram import Router

load_dotenv()

admin_ids = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",")]


class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]):
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


admin_router = Router()
admin_router.message.filter(IsAdmin(admin_ids))