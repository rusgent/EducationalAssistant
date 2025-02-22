from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

from io import BytesIO

send_menu = Router()

@send_menu.message(Command('find_menu'))
async def cmd_find_menu(message: Message):
    await message.answer(f'Ушел искать меню, скоро вернусь босс!')
    url = "https://moausoch3buraevo.02edu.ru/meal/menu/"

    responce = requests.get(url)

# # Функция для получения PDF-файла в память
# def download_pdf_in_memory(pdf_url):
#     response = requests.get(pdf_url)
#     if response.status_code == 200:
#         return response.content
#     return None


# # Функция для конвертации PDF в изображение из памяти
# def pdf_to_image_from_bytes(pdf_bytes):
#     images = convert_from_bytes(pdf_bytes)
#     # Конвертируем первую страницу в изображение
#     img_io = BytesIO()
#     images[0].save(img_io, 'PNG')
#     img_io.seek(0)
#     return img_io

    if responce.status_code == 200:
        soup = BeautifulSoup(responce.text, 'html.parser')

        pdf_link = soup.find('a', class_='mr-1 sf-link sf-link-theme sf-link-dashed')
        data = soup.find('h3', class_="t-1 mt-4")
        if pdf_link and 'href' in pdf_link.attrs and data:
            pdf_url = urljoin(url, pdf_link['href'])
            res_url = quote(pdf_url, safe=':/')

            if res_url:
                await message.answer(f'Дата - {data.text.strip()}\nСсылка на PDF-меню - {res_url}')
                await state.set
            else:
                await message.answer(f'Я не нашел меню!!!')
        else:
            await message.answer(f'Я не нашел меню!!!')

    else:
        await message.answer(f'Я не нашел меню!!!')
    