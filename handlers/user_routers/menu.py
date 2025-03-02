from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .common import *
from handlers.user_routers.texts import *
from handlers.user_routers.states import MarksState
from keyboards import inline_kb


menu_router = Router()

@menu_router.message(Command('school_menu'))
async def get_school_menu(message: Message):
    menu = await Database.get_school_menu_id()
    
    await message.answer_photo(photo=menu.menu_id,
    caption=(
        f"<blockquote><b>📅 Меню столовой на {menu.date}\n</b></blockquote>"
        "📌 Расписание обновляется каждый вечер. Если здесь нет нового меню, значит его еще не опубликовали на сайте, ожидайте 😉\n\n"
        "⚙️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu"
    ))
    
@menu_router.callback_query(F.data == 'school_menu')
async def get_school_menu_ikb(callback: CallbackQuery):
    menu = await Database.get_school_menu_id()
    
    await callback.message.answer_photo(photo=menu.menu_id,
    caption=(
        f"<blockquote><b>📅 Меню столовой на {menu.date}\n</b></blockquote>"
        "📌 Меню обновляется каждый вечер. Если здесь нет нового меню, значит его еще не опубликовали на сайте, ожидайте 😉\n\n"
        "⚙️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu"
    ))
    await callback.answer()
    

@menu_router.message(Command('notif_menu'))
async def edit_notif_menu(message: Message):
    is_notif = int(await Database.check_school_notif_menu(message.from_user.id))
    if is_notif == 1:
        await message.answer(
            "<b>⚙️ У вас в данный момент включена авто-отправка меню каждый вечер\n</b>"
            "Если вы хотите отключить авто-отправку, просто нажмите на кнопку ниже 👇",reply_markup=inline_kb.get_otkl_menu()
        )
    
    elif is_notif == 0:
        await message.answer(
            "<b>⚙️ У вас в данный момент отключена авто-отправка меню каждый вечер\n</b>"
            "Если вы хотите включить авто-отправку, просто нажмите на кнопку ниже 👇",reply_markup=inline_kb.get_vkl_menu()
        )
        
@menu_router.callback_query(F.data.startswith('school_menu_'))
async def cb_otkl_or_vkl_notif(callback: CallbackQuery):
    a, b, is_notif = callback.data.split('_')
    
    if is_notif == 'vkl':
        await Database.edit_vkl_school_notif_menu(callback.message.from_user.id)
        await callback.answer('✔ Вы успешно включили авто-отправка меню', show_alert=True)
        await callback.message.edit_text(text="<b>⚙️ У вас теперь же включена авто-отправка меню каждый вечер\n</b>"
            "Если вы хотите отключить авто-отправку, просто нажмите на кнопку ниже 👇",reply_markup=inline_kb.get_otkl_menu())
    
    elif is_notif == 'otkl':
        await Database.edit_otkl_school_notif_menu(callback.message.from_user.id)
        await callback.answer('✔ Вы успешно отключили авто-отправка меню', show_alert=True)
        await callback.message.edit_text(text="<b>⚙️ У вас теперь же отключена авто-отправка меню каждый вечер\n</b>"
            "Если вы хотите включить авто-отправку, просто нажмите на кнопку ниже 👇",reply_markup=inline_kb.get_vkl_menu())