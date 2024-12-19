from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.user_routers.states import MarksState
from keyboards import inline_kb

middle_mark_router = Router()


@middle_mark_router.callback_query(F.data == "calc_marks")
async def calc_marks_ikb(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    try:
        await callback.message.delete()
    except TelegramBadRequest as e:
        pass

    await cmd_marks(callback.message, state)

    await callback.answer()


@middle_mark_router.message(Command('marks'))
async def cmd_marks(message: Message, state: FSMContext):
    TEXT = (
        '<b>💯 Вы успешно зашли в режим расчета среднего балла</b>\n\n'
        '📋 Список ваших оценок пока что пуст :(\n\n'
        '📊 Ваш средний балл -> 0.0\n\n'
        '👇 Нажимая на кнопки ниже, вы можете добавлять в свой список нужные оценки'
    )

    list_marks = []
    average_mark = 0.0

    await state.update_data(
        list_marks=list_marks,
        average_mark=average_mark)

    await message.answer(text=TEXT,
                         reply_markup=inline_kb.list_2345_marks())

    await state.set_state(MarksState.waiting_add_marks)


@middle_mark_router.callback_query(MarksState.waiting_add_marks)
async def add_marks_cb(callback: CallbackQuery, state: FSMContext):

    add_mark = float(callback.data)

    data = await state.get_data()
    new_marks_list = data['list_marks']
    new_marks_list.append(add_mark)

    new_avg = sum(new_marks_list) / len(new_marks_list) if new_marks_list else 0.0

    target_5_for_4_5 = max(0, (len(new_marks_list) * 4.5 - sum(new_marks_list)) / (5 - 4.5))

    target_5_for_3_5 = max(0, (len(new_marks_list) * 3.5 - sum(new_marks_list)) / (5 - 3.5))

    target_4_for_3_5 = max(0, (len(new_marks_list) * 3.5 - sum(new_marks_list)) / (4 - 3.5))

    marks_display = ' | '.join(str(mark) for mark in new_marks_list) + ' |'

    if new_avg >= 4.50:
        quarter_grade = '5 🟢'
    elif new_avg >= 3.50:
        quarter_grade = '4 🟡'
    elif new_avg >= 2.50:
        quarter_grade = '3 🟠'
    else:
        quarter_grade = '2 🔴'

    TEXT = (
        '<b>💯 Вы успешно зашли в режим расчета среднего балла</b>\n\n'
        f'<b>📋 Список ваших оценок ⬇️\n'
        f'| {marks_display}\n\n'
        f'📊 Ваш средний балл ➡️ {new_avg:.2f}\n'
        f'🔄 Оценка, которая выйдет в четверть: {quarter_grade}</b>\n\n'
        f'📈 Прогноз успеваемости:\n'
        f'🔹 Кол-во 5ок до ср. балла 4.5: {int(target_5_for_4_5)}\n'
        f'🔹 Кол-во 5ок до ср. балла 3.5: {int(target_5_for_3_5)}\n'
        f'🔹 Кол-во 4ок до ср. балла 3.5: {int(target_4_for_3_5)}\n\n'
        '👇 Нажимая на кнопки ниже, вы можете добавлять в свой список нужные оценки'
    )

    await callback.bot.edit_message_text(
        text=TEXT,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_kb.list_2345_marks()
    )

    await state.update_data(
        list_marks=new_marks_list,
        average_mark=new_avg)
