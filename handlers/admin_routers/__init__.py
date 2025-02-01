# from aiogram.filters import BaseFilter
# from dotenv import load_dotenv
# from aiogram.types import Message
# import os
# import logging

# load_dotenv()
# logging.basicConfig(level=logging.INFO)

# admin_ids = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS", "").split(",")]

# class IsAdmin(BaseFilter):
#     def __init__(self, admin_ids: list[int]):
#         self.admin_ids = admin_ids

#     async def __call__(self, message: Message) -> bool:
#         is_admin = message.from_user.id in self.admin_ids
#         logging.info(f"Message from {message.from_user.id}, Is Admin: {is_admin}")
#         return is_admin