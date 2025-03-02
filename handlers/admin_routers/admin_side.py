from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
import datetime
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from pdf2image import convert_from_bytes
import asyncio
import os
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
        "/find_menu - Найти меню\n"
        '/upd_menu_bd - Обновить БД'
    )
    await message.answer(ADMIN_PANEL_TEXT, parse_mode="HTML")
    
    
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
                    caption=(f"<b><blockquote>Меню на {date}</blockquote></b>\n\n"
                        "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                        "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                        "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                        "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                        "<i>Администрация бота желает вам продуктивной недели 😊</i>")
                        )
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
                        caption=(f"<b><blockquote>Меню на {date}</blockquote></b>\n\n"
                        "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n"
                        "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
                        "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!\n\n"
                        "❗️ Вы можете включить/отключить авто-отправку меню с помощью команды - /notif_menu ❗️\n"
                        "<i>Администрация бота желает вам продуктивной недели 😊</i>")
                        )

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