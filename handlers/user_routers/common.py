from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from database.orm import Database
from keyboards import inline_kb

common_router = Router()


@common_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):

    WELCOME_TEXT = (
        f"👋 <b>Привет, {message.from_user.full_name}! 🎉</b>\n\n"
        "Добро пожаловать в <b>🎓 Образовательный Помощник</b>!\n\n"
        "<b>🤖 Этот бот создан для удобства и автоматизации школьных процессов. Вы сможете:</b>\n"
        "<blockquote>🧠 Пройти профориентационный тест и получить рекомендации</blockquote>\n"
        "<blockquote>🧮 Рассчитать свои оценки с помощью калькулятора и узнать, какие оценки нужны для "
        "достижения цели</blockquote>\n"
        "<blockquote>🗃 Получить расписание занятий для своего класса</blockquote>\n\n"
        "<b>👇 Вот что я могу сделать для вас:</b>\n"
        "<blockquote>❓ <b>/help — </b>Получить помощь по использованию бота</blockquote>\n"
        "<blockquote>🧮 <b>/marks — </b>Рассчитать свой средний балл с помощью калькулятора оценок</blockquote>\n"
        "<blockquote>🗃 <b>/shedule — </b>Получить расписание, по своему классу</blockquote>\n"
        "<blockquote>🧠 <b>/test — </b>Пройти тест на профориентацию и получить рекомендации</blockquote>\n"
        "<blockquote>💬 <b>/teh — </b>Cвязаться с тех.поддержкой бота</blockquote>"
    )

    MENU_TEXT = (
        "<b>🎓 Главное Меню 📚</b>\n\n"
        "👉 Выберите одну из опций ниже:\n\n"
        "🧠 <b>Профориентационный тест</b> — Найдите свое призвание\n"
        "🧮 <b>Калькулятор оценок</b> — Рассчитайте свой средний балл\n"
        "🗃 <b>Расписание</b> — Получите расписание по своему классу\n\n"
        "💡 <i>Не знаете, с чего начать? Просто выберите интересующую вас опцию!</i>"
    )

    all_users = await Database.get_all_users()
    all_users_id = [user.id for user in all_users]

    if message.from_user.id not in all_users_id:
        user = message.from_user
        await Database.add_user(user.id, user.username, user.full_name)

    await message.answer_photo(caption=WELCOME_TEXT, photo='https://i.imgur.com/m72muS3.jpeg', reply_markup=ReplyKeyboardRemove())
    await message.answer(MENU_TEXT, parse_mode='HTML', reply_markup=inline_kb.get_menu_ikb())


@common_router.message(Command('menu'))
async def cmd_menu(message: Message, state: FSMContext):

    sent_message = await message.answer(text=".", reply_markup=ReplyKeyboardRemove())
    await message.bot.delete_message(chat_id=message.chat.id, message_id=sent_message.message_id)

    await state.clear()

    MENU_TEXT = (
        "<b>🎓 Главное Меню 📚</b>\n\n"
        "👉 Выберите одну из опций ниже:\n\n"
        "🧠 <b>Профориентационный тест</b> — Найдите свое призвание\n"
        "🧮 <b>Калькулятор оценок</b> — Рассчитайте свой средний балл\n"
        "🗃 <b>Расписание</b> — Получите расписание по своему классу\n\n"
        "💡 <i>Не знаете, с чего начать? Просто выберите интересующую вас опцию!</i>"
    )

    await message.answer(MENU_TEXT, parse_mode='HTML', reply_markup=inline_kb.get_menu_ikb())


@common_router.message(Command('help'))
async def cmd_help(message: Message):

    HELP_TEXT = (
        "👋 <b>Привет!</b> Я — ваш <b>Образовательный Помощник</b> 🎓\n\n"
        "Вот тут представлены все мои команды:\n\n"
        "🔹 <b>/start</b> — Перезапустить/Начать работу с ботом и увидеть главное меню.\n"
        "🔹 <b>/menu</b> — Вызов главного меню.\n"
        "🔹 <b>/marks</b> — Калькулятор оценок для расчета среднего балла.\n"
        "🔹 <b>/shedule</b> — Получить расписание для своего класса.\n"
        "🔹 <b>/test</b> — Пройти профориентационный тест и получить рекомендации.\n"
        "🔹 <b>/favorites</b> — Взаимодействие со списком ваших избранных классов для быстрого доступа к расписанию.\n"
        "🔹 <b>/teh</b> — Связаться с техподдержкой.\n\n"
        "💡 <i>Если у вас возникли вопросы по использованию бота, не стесняйтесь обращаться к техподдержке.</i>"
    )

    await message.answer(HELP_TEXT, parse_mode='HTML')


@common_router.message(Command("teh"))
async def cmd_teh(message: Message):

    TEH_SUPPORT_TEXT = (
        "🛠 <b>Техническая поддержка</b> 🛠\n\n"
        "Если у вас возникли вопросы или трудности при использовании бота, "
        "вы можете обратиться за помощью к нашей техподдержке по ссылке ниже:\n\n"
        "<a href='https://t.me/botdevrus'>💬 Связаться с техподдержкой</a>\n\n"
        "📌 <b>Важно:</b> Просим не спамить в чате и подождать ответа — специалисты ответят вам в ближайшее время. "
        "Ваши вопросы и предложения важны для нас, и мы постараемся помочь как можно скорее.\n\n"
        "💡 <b>Мы всегда открыты к вашим идеям и предложениям!</b> Если у вас есть идеи, как сделать бота ещё лучше, "
        "пожалуйста, поделитесь ими с нами — мы рады слышать ваше мнение!"
    )

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


