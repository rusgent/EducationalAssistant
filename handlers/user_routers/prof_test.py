from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from .common import *
from database.orm import Database
from handlers.user_routers.texts import *
from handlers.user_routers.states import TestStates
from keyboards import inline_kb

prof_test_router = Router()


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

    await callback.message.answer(
        "<b>😁 Смело пересылайте этот результат своим друзьям и знакомым!</b>",
        parse_mode='HTML'
    )


    await callback.message.answer(TEST_RESULT.format(last_result=last_result[0], timestamp=timestamp.strftime('%Y-%m-%d %H:%M:%S'), parse_mode='HTML'))
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

    await callback.message.edit_text(TEST_Q2,
        parse_mode='HTML',
        reply_markup=inline_kb.q2_ikb()
    )
    await state.set_state(TestStates.Q2)


@prof_test_router.callback_query(TestStates.Q2, F.data.startswith('q2_'))
async def handle_q2(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split('_')[1]
    await state.update_data(answer2=answer)

    await callback.message.edit_text(TEST_Q3,
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

    await callback.message.edit_text(TEST_FINISH.format(result=result), parse_mode='HTML', reply_markup=inline_kb.menu_ikb())
    await state.clear()
