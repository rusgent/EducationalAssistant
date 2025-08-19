from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

ikb_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить премиум юзера', callback_data='add_new_prem_user')],
    [InlineKeyboardButton(text='🗑 Удалить премиум юзера', callback_data='del_prem_user')],
    [InlineKeyboardButton(text='👁 Просмотреть лист юзеров', callback_data='check_list_users')]
    
])

ikb_add_new_prem = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить премиум юзера', callback_data='add_new_prem_user')]
    
])

ikb_back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏠 Админ-панель', callback_data='go_back_admin_panel')]
])

kb_money_20 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='20')],
], resize_keyboard=True)

ikb_yes_no = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Активировать', callback_data='res_yes')],
    [InlineKeyboardButton(text='❌ НЕТ', callback_data='res_no')]
])

ikb_del_yes_no = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🗑 Удалить', callback_data='del_yes')],
    [InlineKeyboardButton(text='❌ НЕТ', callback_data='del_no')]
])

ikb_check_normal_or_prem_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Обычные', callback_data='check_normal_users')],
    [InlineKeyboardButton(text='❌ Премиум', callback_data='check_prem_users')]
])