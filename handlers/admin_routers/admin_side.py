from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
import datetime
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from pdf2image import convert_from_bytes
import asyncio
import os
import html
from handlers.user_routers.states import *
from aiogram.fsm.context import FSMContext
from database.orm import Database
from keyboards import inline_kb
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
from io import BytesIO
from aiogram.filters import BaseFilter
from dotenv import load_dotenv
from aiogram.types import Message
import os
import logging
from datetime import datetime, timedelta

import handlers.admin_routers.keyboards as kb
from handlers.admin_routers.states import *

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
#admin_ids = [1006706663, 2084271395]

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
async def cmd_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    """Панель администратора для доступа к функциям управления"""
    ADMIN_PANEL_TEXT = (
        "🔐 <b>Админ-панель</b> 🔐\n\n"
        "Выберите одну из доступных команд:\n\n"
        "📋 <b>/view_users</b> — Просмотреть всех пользователей\n"
        "/find_menu - Найти меню\n"
        '/upd_menu_bd - Обновить БД'
    )
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    await message.answer(ADMIN_PANEL_TEXT, parse_mode="HTML", reply_markup=kb.ikb_menu)
    
@admin_router.callback_query(F.data == 'go_back_admin_panel')
async def cb_admin_panel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    """Панель администратора для доступа к функциям управления"""
    ADMIN_PANEL_TEXT = (
        "🔐 <b>Админ-панель</b> 🔐\n\n"
        "Выберите одну из доступных команд:\n\n"
        "📋 <b>/view_users</b> — Просмотреть всех пользователей\n"
        "/find_menu - Найти меню\n"
        '/upd_menu_bd - Обновить БД'
    )
    sent_message = await callback.message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sent_message.message_id)
    await callback.message.answer(ADMIN_PANEL_TEXT, parse_mode="HTML", reply_markup=kb.ikb_menu)
    await callback.answer()
    
@admin_router.callback_query(F.data == 'add_new_prem_user')
async def add_new_prem_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('❓ Отправь ID юзера, которому нужно АКТИВИРОВАТЬ', reply_markup=kb.ikb_back_menu)
    await state.set_state(AddNewPrem.wait_send_id)
    await callback.answer()
    
@admin_router.message(AddNewPrem.wait_send_id)
async def give_id_new_prem_user(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer('❓ Отправь сколько он тебе перевел', reply_markup=kb.kb_money_20)
    await state.set_state(AddNewPrem.wait_send_money)

@admin_router.message(AddNewPrem.wait_send_money)
async def give_money_new_prem_user(message: Message, state: FSMContext):
    await state.update_data(money=message.text)
    await state.update_data(days=(int(message.text)/20)*30)

    data = await state.get_data()
    money = data['money']
    user_id = data['user_id']
    days = data['days']

    user = await Database.check_user(int(user_id))
    user_prem = await Database.check_in_premium_users_table(int(user_id))
    
    if not user:
        await message.answer(f'❌ Данный пользователь был не найден в базе данных!\nID - {user_id}', reply_markup=kb.ikb_back_menu)
        
    elif user_prem:
        await message.answer((f'❌ У данного пользователя {user_prem.fullname} уже активирована премка!\n'
                              f'ID - {user_prem.tg_id} | @{user_prem.username}\n\n'
                              f'Подписка активна до {(user_prem.premium_end_date).strftime("%d.%m.%Y")}'),
                             reply_markup=kb.ikb_back_menu)
        
    
    else:
        await message.answer((f'🚩 Пользователь {user.fullname} был успешно найден!\n'
                              f'ID - {user.user_id} | @{user.username}\n\n'
                              f'Подписка будет активна до {(datetime.now() + timedelta(int(days))).date().strftime("%d.%m.%Y")}'),
                             reply_markup=kb.ikb_yes_no)
        
@admin_router.callback_query(F.data.startswith('res_'))
async def cb_yes_no(callback: CallbackQuery, state: FSMContext, bot: Bot):
    a, res = callback.data.split('_')

    if res == 'yes':
            data = await state.get_data()
            money = int(data['money'])
            user_id = int(data['user_id'])
            days = int(data['days'])

            user = await Database.check_user(int(user_id))
            if user:
                await callback.message.answer((f'✅ Пользователю {user.fullname} была УСПЕШНО ВЫДАНА ПРЕМКА!\n'
                                    f'ID - {user.user_id} | @{user.username}\n\n'
                                    f'Подписка будет активна до {(datetime.now() + timedelta(int(days))).date().strftime("%d.%m.%Y")}'),
                                    reply_markup=kb.ikb_menu)

                await Database.add_new_prem_user(user_id, user.username, user.fullname,
                                                (datetime.now() + timedelta(int(days))).date(),
                                                bot, money, days)

                await bot.send_message(chat_id=user_id,text = (
                                            f"<b>🎉 Ура! Ваша подписка активирована на {days} дней до {(datetime.now() + timedelta(int(days))).date().strftime('%d.%m.%Y')} за {money} рублей!\n\n</b>"
                                            "Теперь тебе доступны все возможности нашего школьного помощника:\n"
                                            "<i>📚 Удобное расписание\n"
                                            "🧮 Умный калькулятор оценок\n"
                                            "⭐ Избранные классы и многое другое\n"
                                            "🚀 И новые функции, которые будут выходить только для премиум-пользователей!</i>\n\n"
                                            "<b>Спасибо, что ты с нами ❤️</b>"
                                        ))

    elif res == 'no':
        await callback.message.answer('❌ Отмена!', reply_markup=kb.ikb_back_menu)
        
@admin_router.callback_query(F.data == 'del_prem_user')
async def cb_del_prem_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('❓ Отправь ID премиум-юзера, которому нужно УДАЛИТЬ из таблицы премиум-юзеров', reply_markup=kb.ikb_back_menu)
    await state.set_state(DelPrem.wait_send_id)
    await callback.answer()


@admin_router.message(DelPrem.wait_send_id)
async def send_id_del_prem(message: Message, state: FSMContext):
    user_id = message.text
    await state.update_data(user_id=message.text)
    user_prem = await Database.check_in_premium_users_table(int(user_id))
    await state.update_data(user_prem=user_prem)
    if not user_prem:
        await message.answer(f'❌ Данный пользователь был не найден в базе данных премиум-юзеров!\nID - {user_id}', reply_markup=kb.ikb_back_menu)
        
    elif user_prem:
        await message.answer((f'🚩 У данного пользователя {user_prem.fullname} активирована премка!\n'
                              f'ID - {user_prem.tg_id} | @{user_prem.username}\n\n'
                              f'Подписка активна до {(user_prem.premium_end_date).strftime("%d.%m.%Y")}\n'
                              'Вы точно хотите его УДАЛИТЬ с БД премиум-юзеров???'),
                             reply_markup=kb.ikb_del_yes_no)


@admin_router.callback_query((F.data == 'del_yes') | (F.data == 'del_no'))
async def yes_no_del_prem(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = int(data['user_id'])
    user_prem = data['user_prem']
    
    if callback.data == 'del_yes':
        await Database.del_prem_user(user_id)
        await callback.message.answer((f'🗑 Данный пользователь {user_prem.fullname} был успешно УДАЛЕН!\n'
                              f'ID - {user_prem.tg_id} | @{user_prem.username}\n\n'
                              f'Подписка активна была до {(user_prem.premium_end_date).strftime("%d.%m.%Y")}\n'
                              ),
                             reply_markup=kb.ikb_back_menu)
        

    elif callback.data == 'del_no':
        await callback.message.answer((f'❌ Отмена УДАЛЕНИЯ премиум-юзера'),
                             reply_markup=kb.ikb_back_menu)
    
    await callback.answer()
    
@admin_router.callback_query(F.data == 'check_list_users')
async def cb_check_list_users(callback: CallbackQuery):
    await callback.message.edit_text("❗️ Выберите каких юзеров будем чекать :)", reply_markup=kb.ikb_check_normal_or_prem_users)
    await callback.answer()
    
@admin_router.callback_query((F.data == 'check_normal_users') | (F.data == 'check_prem_users'))
async def check_lists_users(callback: CallbackQuery):
    if callback.data == 'check_normal_users':
            users = await Database.get_all_users()
            user_count = len(users)

            if users:
                user_list = "\n".join([f"ID: <code>{user.user_id}</code>, Username: @{html.escape(user.username or '—')}, Имя: {html.escape(user.fullname or '—')}" for user in users])

                # Проверка длины сообщения и разбиение, если превышает лимит
                max_message_length = 4000
                if len(user_list) > max_message_length:
                    # Разбиваем список на части
                    chunks = [user_list[i:i + max_message_length] for i in range(0, len(user_list), max_message_length)]
                    for chunk in chunks:
                        await callback.message.answer(
                            f"📋 <b>Список пользователей:</b>\n\n{chunk}\n\n"
                            f"🔢 <b>Всего зарегистрировано пользователей:</b> {user_count}"
                        )
                else:
                    # Если сообщение помещается в один раз, отправляем его целиком
                    await callback.message.answer(
                        f"📋 <b>Список пользователей:</b>\n\n{user_list}\n\n"
                        f"🔢 <b>Всего зарегистрировано пользователей:</b> {user_count}"
                    )
            else:
                await callback.message.answer("❗ Пользователи не найдены в базе данных.")
            
    elif callback.data == 'check_prem_users':
            users = await Database.get_all_prem_users()
            user_count = len(users)

            if users:
                user_list = "\n".join([f"ID: <code>{user.tg_id}</code>, Username: @{html.escape(user.username or '—')}, Имя: {html.escape(user.fullname or '—')}" for user in users])

                # Проверка длины сообщения и разбиение, если превышает лимит
                max_message_length = 4000
                if len(user_list) > max_message_length:
                    # Разбиваем список на части
                    chunks = [user_list[i:i + max_message_length] for i in range(0, len(user_list), max_message_length)]
                    for chunk in chunks:
                        await callback.message.answer(
                            f"📋 <b>Список пользователей:</b>\n\n{chunk}\n\n"
                            f"🔢 <b>Всего премиум-пользователей:</b> {user_count}"
                        )
                else:
                    # Если сообщение помещается в один раз, отправляем его целиком
                    await callback.message.answer(
                        f"📋 <b>Список пользователей:</b>\n\n{user_list}\n\n"
                        f"🔢 <b>Всего премиум-пользователей:</b> {user_count}"
                    )
            else:
                await callback.message.answer("❗ Пользователи не найдены в базе данных.")
    

@admin_router.message(Command("testmenu"))
async def cmd_test(message: Message):
        await message.answer(text = (
                        "🔥 <b>Внимание! Бот отключится в 00:00!</b> 🔥\n\n"
                        "⏳ Время на исходе! Успей протестировать новые функции, пока бот ещё работает.\n\n"
                        "🚀 <b>Что нового?</b> Заходи в <b>меню (/menu) </b>, выбирай раздел и пробуй сам!\n\n"
                        "⚡ <b>Спеши, пока не поздно!</b> После 12ти бот уходит на отдых 😏\n\n"
                        "<i>🔧 Мы уже работаем над возможностью отключать рассылку меню по вашим запросам. Скоро будет доступно!</i>"
                    ))
        
@admin_router.message(Command('del'))
async def cmd_del_user(message: Message, command: CommandObject):
    user_id = int(command.args)
    a = await Database.del_user(user_id)
    if a:
        await message.answer(f"✅✅✅ Пользователь \nID: {user_id} заблокировал бота и он был успешно удален из БД.")
    else:
        await message.answer(f"❌ НЕ УДАЛОСЬ!!!! Пользователь \nID: {user_id} заблокировал бота и он НЕ был успешно удален из БД.")


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
        
        
 # Функция для получения PDF-файла в память
def download_pdf_in_memory(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        return response.content
    return None


# Функция для конвертации PDF в изображение из памяти
def pdf_to_image_from_bytes(pdf_bytes):
    images = convert_from_bytes(pdf_bytes)
    # Конвертируем первую страницу в изображение
    img_io = BytesIO()
    images[0].save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

@admin_router.message(Command('upd_menu_bd'))
async def cmd_upd_menu(message: Message, state: FSMContext):
    await message.answer(f'Ушел искать меню для обновления в бд, скоро вернусь босс!')
    url = "https://moausoch3buraevo.02edu.ru/meal/menu/"

    responce = requests.get(url)

    if responce.status_code == 200:
        soup = BeautifulSoup(responce.text, 'html.parser')

        pdf_link = soup.find('a', class_='mr-1 sf-link sf-link-theme sf-link-dashed')
        data = soup.find('h3', class_="t-1 mt-4")
        if pdf_link and 'href' in pdf_link.attrs and data:
            pdf_url = urljoin(url, pdf_link['href'])
            res_url = quote(pdf_url, safe=':/')
            await state.update_data({"data": data.text.strip()})
            if res_url:
                await message.answer(f'Дата - {data.text.strip()}\nСсылка на PDF-меню - {res_url}')
                await state.set_state(SendMenu.wait_photo_to_bd)
            else:
                await message.answer(f'Я не нашел меню!!!')
        else:
            await message.answer(f'Я не нашел меню!!!')

    else:
        await message.answer(f'Я не нашел меню!!!')

@admin_router.message(SendMenu.wait_photo_to_bd)
async def get_photo_to_upd_meu(message: Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        date = data.get('data')
        await Database.edit_school_menu_id(photo_id, date=date)
        await message.answer((f"✅ Запись в БД успешно записана\n"
                               f"Photo_id - {photo_id}\n"
                               f"Date - {date}"))


@admin_router.message(Command('find_menu'))
async def cmd_find_menu(message: Message, state: FSMContext):
    await message.answer(f'Ушел искать меню, скоро вернусь босс!')
    url = "https://moausoch3buraevo.02edu.ru/meal/menu/"

    responce = requests.get(url)

    if responce.status_code == 200:
        soup = BeautifulSoup(responce.text, 'html.parser')

        pdf_link = soup.find('a', class_='mr-1 sf-link sf-link-theme sf-link-dashed')
        data = soup.find('h3', class_="t-1 mt-4")
        if pdf_link and 'href' in pdf_link.attrs and data:
            pdf_url = urljoin(url, pdf_link['href'])
            res_url = quote(pdf_url, safe=':/')
            await state.update_data({"data": data.text.strip()})
            if res_url:
                await message.answer(f'Сегодняшняя Дата - {datetime.datetime.now().strftime("%Y-%m-%d")}\nДата - {data.text.strip()}\nСсылка на PDF-меню - {res_url}')
                await state.set_state(SendMenu.wait_photo)
            else:
                await message.answer(f'Я не нашел меню!!!')
        else:
            await message.answer(f'Я не нашел меню!!!')

    else:
        await message.answer(f'Я не нашел меню!!!')
        
@admin_router.message(SendMenu.wait_photo)
async def get_photo(message: Message, state: FSMContext):
    if message.photo:
        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        date = data.get('data')
        await message.answer_photo(
                    photo=photo_id,
                            #caption = (f"<b><blockquote>Меню на {date}</blockquote></b>\n"
                            caption = (f"<b><blockquote>Меню на 20.05.2025</blockquote></b>\n"
                            #"<b>❗️ БОТ РАБОТАЕТ 24/7, можете смело советовать бота своим друзьям ❗️</b>\n\n"
                            "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                            "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                            "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                            "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                            "<i>Администрация бота желает вам продуктивной недели 😊</i>\n\n"
                            "📚 <b>До конца учёбы осталось всего 4 учебных дней!</b>\n"
                            "<i>Скоро каникулы, держитесь — финальный рывок! 💪 Удачи и хорошего настроения ✨</i>"))
                    
                    # caption = (f"<b><blockquote>Меню на {date}</blockquote></b>\n"
                    #         #"<b>❗️ БОТ РАБОТАЕТ 24/7, можете смело советовать бота своим друзьям ❗️</b>\n\n"
                    #         "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                    #         "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                    #         "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                    #         "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                    #         "<i>Администрация бота желает вам продуктивной недели 😊</i>\n\n"
                    #         "📚 <b>До конца учёбы осталось всего 13 дней!</b>\n"
                    #         "<i>Скоро каникулы, держитесь — финальный рывок! 💪 Удачи и хорошего настроения ✨</i>"))
        await message.answer_photo(photo=photo_id, caption='Вы желаете данную фотографию разослать всем юзерам?')
        await state.update_data(photo_id=photo_id)
        await state.set_state(SendMenu.wait_yes)
        
@admin_router.message(SendMenu.wait_yes)
async def send_menu_users(message: Message, state: FSMContext, bot: Bot):
    failed_count = 0
    success_count = 0
    zabl_count = 0
    if message.text == '1':
        data = await state.get_data()
        photo_id = data.get('photo_id')
        date = data.get('data')
        await Database.edit_school_menu_id(photo_id, date=date)
        await message.answer((f"✅ Запись в БД успешно записана\n"
                               f"Photo_id - {photo_id}\n"
                               f"Date - {date}"))
        
        users_list = await Database.get_all_users()
            
        for user in users_list:
            user_info = (f"ID: {user.user_id}\n"
                        f"Username: @{user.username}\n"
                         f"Имя: {user.fullname}")
            if int(user.is_notif) == 1:
                try:
                    await bot.send_photo(
                        chat_id=user.user_id,
                        photo=photo_id,
                            #caption = (f"<b><blockquote>Меню на {date}</blockquote></b>\n"
                            caption = (f"<b><blockquote>Меню на 20.05.2025</blockquote></b>\n"
                            #"<b>❗️ БОТ РАБОТАЕТ 24/7, можете смело советовать бота своим друзьям ❗️</b>\n\n"
                            "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                            "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                            "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                            "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                            "<i>Администрация бота желает вам продуктивной недели 😊</i>\n\n"
                            "📚 <b>До конца учёбы осталось всего 4 учебных дней!</b>\n"
                            "<i>Скоро каникулы, держитесь — финальный рывок! 💪 Удачи и хорошего настроения ✨</i>"))

                        
                        # caption = (f"<b><blockquote>Меню на {date}</blockquote></b>\n"
                        #     #"<b>❗️ БОТ РАБОТАЕТ 24/7, можете смело советовать бота своим друзьям ❗️</b>\n\n"
                        #     "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                        #     "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                        #     "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                        #     "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                        #     "<i>Администрация бота желает вам продуктивной недели 😊</i>\n\n"
                        #     "📚 <b>До конца учёбы осталось всего 13 дней!</b>\n"
                        #     "<i>Скоро каникулы, держитесь — финальный рывок! 💪 Удачи и хорошего настроения ✨</i>"))

                    # await bot.send_message(
                    # chat_id=user.user_id,
                    # text = (
                    #         "🔥 <b>Внимание! Бот отключится в 00:00!</b> 🔥\n\n"
                    #         "⏳ Время на исходе! Успей протестировать новые функции, пока бот ещё работает.\n\n"
                    #         "🚀 <b>Что нового?</b> Заходи в <b>меню (/menu) </b>, выбирай раздел и пробуй сам!\n\n"
                    #         "⚡ <b>Спеши, пока не поздно!</b> После 12ти бот уходит на отдых 😏\n\n"
                    #         "<i>🔧 Мы уже работаем над возможностью отключать рассылку меню по вашим запросам. Скоро будет доступно!</i>"
                    #     ))


                    await asyncio.sleep(0.7)
                    await bot.send_message(1006706663, f"✅ Успешно отправлено:\n{user_info}")
                    success_count += 1
                    await asyncio.sleep(0.7)  # Интервал между отправками

                except TelegramForbiddenError:
                    failed_count += 1
                    a = await Database.del_user(int(user.user_id))
                    if a:
                        await bot.send_message(1006706663,f"⚠⚠⚠ Пользователь \nID: {user.user_id}\nUsername: @{user.username}\nИмя: {user.fullname} заблокировал бота и он был успешно удален из БД.")
                    else:
                        await bot.send_message(1006706663,f"❌ НЕ УДАЛОСЬ!!!! Пользователь \nID: {user.user_id} заблокировал бота и он НЕ был успешно удален из БД.")
                    
                except TelegramRetryAfter as e:
                    await bot.send_message(1006706663, f"⏳ Превышен лимит запросов! Жду {e.retry_after} сек.")
                    await asyncio.sleep(e.retry_after)  # Ждём, если превысили лимит запросов
                    
                except Exception as e:
                    failed_count += 1
                    await bot.send_message(1006706663, f"⚠ Ошибка при отправке пользователю \nID: {user.user_id}\nUsername: @{user.username}\nИмя: {user.fullname}: {e}")
            elif int(user.is_notif) == 0:
                zabl_count += 1

            # Сообщаем админу итог рассылки
        await bot.send_message(1006706663, f"✅ Рассылка завершена!\n"
                                            f"✔ Успешно: {success_count}\n"
                                            f"❌ Ошибок: {failed_count}\n"
                                            f"Откл рассылку {zabl_count}")

        await state.clear()
    elif message.text == '0':
        await state.clear()
        await bot.send_message(1006706663, f"ОТМЕНА братишка)\n")
        
        
        
@admin_router.message(Command('kan'))
async def send_kan(message: Message, state: FSMContext, bot: Bot):
    users_list = await Database.get_all_users()
        
    failed_count = 0
    success_count = 0
    zabl_count = 0
    
    await bot.send_message(chat_id=1006706663,
                           text = (f"<b>Вот и всё — учебный год подошёл к концу 🎓</b>\n"
                            "<b>Спасибо, что были с нами всё это время ❤️</b>\n\n"
                            "📚 9ым и 11ым удачи на экзаменах — вы точно справитесь!\n"
                            "🌈 Желаем вам яркого, тёплого и беззаботного лета.\n"
                            "Пусть будет побольше отдыха, солнца и весёлых моментов!\n\n"
                            "<i>А мы вернёмся в новом учебном году — ещё лучше 💪</i>"))
    
    for user in users_list:
        user_info = (f"ID: {user.user_id}\n"
                        f"Username: @{user.username}\n"
                        f"Имя: {user.fullname}")
        if int(user.is_notif) == 1:
            try:
                await bot.send_message(
                    chat_id=user.user_id,
                    text = (f"<b>Вот и всё — учебный год подошёл к концу 🎓</b>\n"
                            "<b>Спасибо, что были с нами всё это время ❤️</b>\n\n"
                            "📚 9ым и 11ым удачи на экзаменах — вы точно справитесь!\n"
                            "🌈 Желаем вам яркого, тёплого и беззаботного лета.\n"
                            "Пусть будет побольше отдыха, солнца и весёлых моментов!\n\n"
                            "<i>А мы вернёмся в новом учебном году — ещё лучше 💪</i>"))


                # await bot.send_message(
                # chat_id=user.user_id,
                # text = (
                #         "🔥 <b>Внимание! Бот отключится в 00:00!</b> 🔥\n\n"
                #         "⏳ Время на исходе! Успей протестировать новые функции, пока бот ещё работает.\n\n"
                #         "🚀 <b>Что нового?</b> Заходи в <b>меню (/menu) </b>, выбирай раздел и пробуй сам!\n\n"
                #         "⚡ <b>Спеши, пока не поздно!</b> После 12ти бот уходит на отдых 😏\n\n"
                #         "<i>🔧 Мы уже работаем над возможностью отключать рассылку меню по вашим запросам. Скоро будет доступно!</i>"
                #     ))


                await asyncio.sleep(0.7)
                await bot.send_message(1006706663, f"✅ Успешно отправлено:\n{user_info}")
                success_count += 1
                await asyncio.sleep(0.7)  # Интервал между отправками

            except TelegramForbiddenError:
                failed_count += 1
                a = await Database.del_user(int(user.user_id))
                if a:
                    await bot.send_message(1006706663,f"⚠⚠⚠ Пользователь \nID: {user.user_id}\nUsername: @{user.username}\nИмя: {user.fullname} заблокировал бота и он был успешно удален из БД.")
                else:
                    await bot.send_message(1006706663,f"❌ НЕ УДАЛОСЬ!!!! Пользователь \nID: {user.user_id} заблокировал бота и он НЕ был успешно удален из БД.")
                
            except TelegramRetryAfter as e:
                await bot.send_message(1006706663, f"⏳ Превышен лимит запросов! Жду {e.retry_after} сек.")
                await asyncio.sleep(e.retry_after)  # Ждём, если превысили лимит запросов
                
            except Exception as e:
                failed_count += 1
                await bot.send_message(1006706663, f"⚠ Ошибка при отправке пользователю \nID: {user.user_id}\nUsername: @{user.username}\nИмя: {user.fullname}: {e}")
                
    await bot.send_message(1006706663, f"✅ Рассылка завершена!\n"
                                            f"✔ Успешно: {success_count}\n"
                                            f"❌ Ошибок: {failed_count}\n"
                                            f"Откл рассылку {zabl_count}")