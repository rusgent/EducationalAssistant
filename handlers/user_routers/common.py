from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from database.orm import Database

from keyboards import inline_kb, reply_kb
from .texts import *
from .states import *

common_router = Router()


@common_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):

    await Database.add_user_and_check_new_username(
        user_id=message.from_user.id,
        username=message.from_user.username,
        fullname=message.from_user.full_name,
        bot=bot
    )

    await message.answer_photo(caption=WELCOME_TEXT.format(full_name=message.from_user.full_name), photo='https://i.imgur.com/m72muS3.jpeg', reply_markup=ReplyKeyboardRemove())
    await message.answer(MENU_TEXT, parse_mode='HTML', reply_markup=inline_kb.get_menu_ikb())


@common_router.message(Command('menu'))
async def cmd_menu(message: Message, state: FSMContext):

    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)

    await state.clear()

    await message.answer(MENU_TEXT, parse_mode='HTML', reply_markup=inline_kb.get_menu_ikb())


@common_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, parse_mode='HTML')


@common_router.message(Command("teh"))
async def cmd_teh(message: Message):
    await message.answer(TEH_SUPPORT_TEXT, parse_mode='HTML', disable_web_page_preview=True)


@common_router.callback_query(F.data == 'help')
async def cb_help(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await cmd_help(callback.message)
    await callback.answer()


@common_router.callback_query(F.data == "menu")
async def menu_ikb(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest as e:
        pass

    await cmd_menu(callback.message, state)

    await callback.answer()


@common_router.message(Command('favorites'))
async def cmd_favorites(message: Message, state: FSMContext):

    await state.clear()
    send_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())

    await message.bot.delete_message(chat_id=message.chat.id, message_id=send_message.message_id)

    text = (
        f"🤫<b> Избранные классы помогают вам быстрее получить расписание по вашему классу</b>\n\n"
        "❤ Ваши избранные классы:\n"
    )

    list_favcls = await Database.get_favcls_list(message.from_user.id)

    if list_favcls:
        for cls in list_favcls:
            text += f'<i>• {cls}</i>\n'

    else:
        text += '<i>☹ У вас нету избранных классов</i>'



    await message.answer(
        text,
        reply_markup=inline_kb.get_del_or_add_favcls_or_menu(),
        parse_mode='HTML'
    )
    
    
@common_router.message(Command('marks'))
async def cmd_marks(message: Message, state: FSMContext):
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)

    list_marks = []
    average_mark = 0.0

    await state.update_data(
        list_marks=list_marks,
        average_mark=average_mark)

    await message.answer(text=TEXT_MARKS,
                         reply_markup=inline_kb.list_2345_marks())

    await state.set_state(MarksState.waiting_add_marks)



@common_router.message(Command('test'))
async def start_test(message: Message, state: FSMContext):
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    
    await message.answer(text=TEST_Q1,
        parse_mode='HTML',
        reply_markup=inline_kb.q1_ikb()
    )
    await state.set_state(TestStates.Q1)
    
@common_router.message(Command('view_results'))
async def cmd_view_results(message: Message):
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    
    rows = await Database.check_result(message.from_user.id)

    if not rows:
        await message.answer(
            "<b>🚫 Вы еще не проходили тест.</b>\nПожалуйста, пройдите тест, чтобы увидеть результаты.",
            parse_mode='HTML'
        )
        return


    results_message = "<b>📋 Ваши предыдущие результаты:</b>\n\n"
    for row in rows:
        result, timestamp = row
        results_message += (
            f"✅ <b>Результат: {result}</b> <i>(Дата и время: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i>)\n"
        )


    await message.answer(results_message, parse_mode='HTML', reply_markup=inline_kb.share_ikb())
    
    
@common_router.message(Command('shedule'))
async def get_shedule_and_give_num(message: Message, state: FSMContext, user_id: int = None):
    
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    
    await state.clear()

    await state.set_state(GiveSchedule.slctnum)

    await message.answer(
        TEXT_SHEDULE_GIVE_NUMBER,
        reply_markup= await reply_kb.kb_select_class_num(),
        parse_mode='HTML'
    )

    user_id = user_id or message.from_user.id

    favcls_list = await Database.get_favcls_list(user_id)

    if favcls_list:
        await message.answer("❤ Выберите класс из избранных 👇", reply_markup=inline_kb.get_favcls_ikb(favcls_list))


@common_router.message(Command('todo'))
async def cmd_todo(message: Message, state: FSMContext):
    sent_message = await message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)
    
    await state.clear()

    await message.answer(text=TEXT_INFO_TREKER, reply_markup=inline_kb.get_todo_ikb())