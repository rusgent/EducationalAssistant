from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from .common import *
from handlers.user_routers.texts import *
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


    await callback.bot.edit_message_text(
        text=TEXT_LIST_MARKS.format(marks_display=marks_display,
                                    quarter_grade=quarter_grade,
                                    new_avg=f"{new_avg:.2f}",
                                    target_4_for_3_5=int(target_4_for_3_5),
                                    target_5_for_3_5=int(target_5_for_3_5),
                                    target_5_for_4_5=int(target_5_for_4_5)),
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=inline_kb.list_2345_marks()
    )

    await state.update_data(
        list_marks=new_marks_list,
        average_mark=new_avg)
