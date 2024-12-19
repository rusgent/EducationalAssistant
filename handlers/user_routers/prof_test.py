from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.orm import Database
from handlers.user_routers.states import TestStates
from keyboards import inline_kb

prof_test_router = Router()


@prof_test_router.message(Command('test'))
async def start_test(message: Message, state: FSMContext):
    await message.answer(
        "<b>📝 Начнем тест!</b>\n\n"
        "<b>Вопрос 1️⃣:</b> Какую деятельность вы предпочитаете?\n\n"
        "<b>👥 Работать с людьми</b> — Взаимодействовать и сотрудничать с другими.\n"
        "<b>🔧 Работать с техникой</b> — Управлять и обслуживать технические устройства.\n"
        "<b>🗂️ Работать с информацией</b> — Собирать и обрабатывать данные.\n\n"
        "👇 Выберите один из вариантов",
        parse_mode='HTML',
        reply_markup=inline_kb.q1_ikb()
    )
    await state.set_state(TestStates.Q1)


@prof_test_router.message(Command('view_results'))
async def cmd_view_results(message: Message):
    rows = await Database.check_result(message.from_user.id)

    if not rows:
        await message.answer(
            "<b>🚫 Вы еще не проходили тест.</b>\nПожалуйста, пройдите тест, чтобы увидеть результаты.",
            parse_mode='HTML'
        )
        return


    results_message = "<b>📋 Ваши предыдущие результаты:</b>\n\n"
    print(rows)
    for row in rows:
        result, timestamp = row
        results_message += (
            f"✅ <b>Результат: {result}</b> <i>(Дата и время: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i>)\n"
        )


    await message.answer(results_message, parse_mode='HTML', reply_markup=inline_kb.share_ikb())


@prof_test_router.callback_query(F.data == 'share_result')
async def cb_share_result(callback: CallbackQuery):
    user_id = callback.from_user.id

    result = await Database.check_result(user_id)

    if not result:
        await callback.message.answer(
            "<b>🚫 У вас нет сохраненных результатов для пересылки.</b>",
            parse_mode='HTML'
        )
        return

    last_result = result[-1]
    timestamp = last_result[1]
    result_text = (
        f"📊 <b>Ваш результат -  <i>{last_result[0]}</i></b>\n"
        f"📅 <b>Дата и время - <i>{timestamp.strftime('%Y-%m-%d %H:%M:%S')}</i></b>\n\n"
        "🎓 <b>Пройдите</b> и вы тест в нашем <b>школьном боте</b> и получите рекомендации, подходящие именно вам!\n"
        "🔗 <b>Ссылка на школьного бота</b> - https://t.me/moau3byr_bot"
    )

    await callback.message.answer(
        "<b>😁 Смело пересылайте этот результат своим друзьям и знакомым!</b>",
        parse_mode='HTML'
    )


    await callback.message.answer(result_text, parse_mode='HTML')
    await callback.answer()


@prof_test_router.callback_query(F.data == "test")
async def test_ikb(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await start_test(callback.message, state)

    await callback.answer()


@prof_test_router.callback_query(TestStates.Q1, F.data.startswith('q1_'))
async def handle_q1(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split('_')[1]
    await state.update_data(answer1=answer)

    await callback.message.edit_text(
        "<b>🔍 Вопрос 2️⃣:</b> Что вам больше нравится?\n\n"
        "<b>📊 Анализировать данные</b> — Анализировать информацию и находить закономерности.\n"
        "<b>🛠️ Создавать что-то новое</b> — Изобретать и воплощать новые идеи.\n"
        "<b>💬 Общаться с людьми</b> — Взаимодействовать с другими.\n\n"
        "👇 Выберите один из вариантов",
        parse_mode='HTML',
        reply_markup=inline_kb.q2_ikb()
    )
    await state.set_state(TestStates.Q2)


@prof_test_router.callback_query(TestStates.Q2, F.data.startswith('q2_'))
async def handle_q2(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split('_')[1]
    await state.update_data(answer2=answer)

    await callback.message.edit_text(
        "<b>💡 Вопрос 3️⃣:</b> Какой вид деятельности вам интересен?\n\n"
        "<b>🔬 Научные исследования</b> — Проводить исследования и анализировать данные.\n"
        "<b>🎨 Творчество и искусство</b> — Создавать и выражать себя через искусство.\n"
        "<b>⚙️ Техническое обеспечение</b> — Обеспечивать поддержку и решать технические задачи.\n\n"
        "👇 Выберите один из вариантов",
        parse_mode='HTML',
        reply_markup=inline_kb.q3_ikb()
    )
    await state.set_state(TestStates.Q3)


@prof_test_router.callback_query(TestStates.Q3, F.data.startswith('q3_'))
async def handle_q3(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split('_')[1]
    await state.update_data(answer3=answer)

    user_data = await state.get_data()
    result = inline_kb.calculate_result(user_data)

    user_id = callback.from_user.id

    await Database.save_result(user_id, result)

    final_message = (
        "<b>✅ Тест завершен!</b>\n\n"
        f"<b>💡 Ваша рекомендация: <i>{result}</i></b>\n\n"
        "<b>🔍 Вы можете просмотреть свои прошлые результаты по команде:</b> /view_results\n\n"
        "<b>📄 Если у вас есть вопросы или вы хотите пройти тест снова, просто напишите:</b> /test"
    )

    await callback.message.edit_text(final_message, parse_mode='HTML', reply_markup=inline_kb.menu_ikb())
    await state.clear()
