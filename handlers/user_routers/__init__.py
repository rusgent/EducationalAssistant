from aiogram import Router
from .common import common_router
from .favcls import favcls_router
from .middle_mark import middle_mark_router
from .prof_test import prof_test_router
from .shedule import shedule_router
from .todo import todo_router
from .menu import menu_router
from handlers.middlewares import CheckMiddleware

user_router = Router()

user_router.inline_query.middleware(CheckMiddleware())
user_router.callback_query.middleware(CheckMiddleware())
user_router.message.middleware(CheckMiddleware())

user_router.include_routers(
    common_router, menu_router, favcls_router, shedule_router,
    prof_test_router, middle_mark_router, todo_router,
    )