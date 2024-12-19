from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.sqlite import *
import asyncio

# def group_keyboard(group_list):
#     # Если список пуст, создаем пустую клавиатуру
#     if not group_list:
#         return ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)

#     # Извлекаем только названия групп (первый элемент кортежа)
#     buttons = [[KeyboardButton(text=group[0])] for group in group_list]

#     # Создаем клавиатуру с кнопками
#     kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
#     return kb


async def kb_select_class_num():
    # Получаем список классов
    cls_list = [5, 6, 7, 8, 9, 10, 11]

    kb = ReplyKeyboardBuilder()

    # Создаем клавиатуру

    # Добавляем кнопки для каждого класса
    for cls in cls_list:
        kb.add(KeyboardButton(text=str(cls)))

    # Настраиваем количество кнопок в строке (если нужно)
    kb = kb.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True) # Это сделает три кнопки в строке

    return kb


async def kb_select_class_lit():
    # Получаем список классов
    cls_list = ['А', 'Б', 'В', 'Ш', 'П']  # Убедитесь, что используются русские буквы

    kb = ReplyKeyboardBuilder()

    # Создаем клавиатуру
    for cls in cls_list:
        kb.add(KeyboardButton(text=cls))

    # Настраиваем количество кнопок в строке (если нужно)
    kb = kb.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True)  # Это сделает три кнопки в строке

    return kb


