from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def kb_select_class_num():
    cls_list = [5, 6, 7, 8, 9, 10, 11]

    kb = ReplyKeyboardBuilder()

    for cls in cls_list:
        kb.add(KeyboardButton(text=str(cls)))

    kb = kb.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True)

    return kb


async def kb_select_class_lit():

    cls_list = ['А', 'Б', 'В', 'Ш', 'П']

    kb = ReplyKeyboardBuilder()

    for cls in cls_list:
        kb.add(KeyboardButton(text=cls))

    kb = kb.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True)

    return kb


