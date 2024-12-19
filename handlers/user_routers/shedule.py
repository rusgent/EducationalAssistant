from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from database.orm import Database
from handlers.user_routers.common import cmd_menu
from handlers.user_routers.states import GiveSchedule
from keyboards import reply_kb, inline_kb


shedule_router = Router()


@shedule_router.message(Command('shedule'))
async def get_shedule_and_give_num(message: Message, state: FSMContext, user_id: int = None):
    await state.clear()

    await state.set_state(GiveSchedule.slctnum)

    text = (
        f"📅 <b>Введите номер класса</b> — "
        "<i>нажмите на соответствующую кнопку под полем ввода или введите номер класса вручную"
        "(например, 9A или 10А)</i>\n\n"
        "👇 <b>Вы также быстро можете выбрать класс из своих избранных классов, "
        "нажав на кнопку под следующим сообщением\n\n"
        "🗂 Добавить класс в избранное по команде —> /favorites</b>"

    )

    await message.answer(
        text,
        reply_markup= await reply_kb.kb_select_class_num(),
        parse_mode='HTML'
    )

    user_id = user_id or message.from_user.id

    favcls_list = await Database.get_favcls_list(user_id)

    if favcls_list:
        await message.answer("❤ Выберите класс из избранных 👇", reply_markup=inline_kb.get_favcls_ikb(favcls_list))


@shedule_router.callback_query(F.data.in_(["schedule", "new_schedule"]))
async def shedule_ikb(callback: CallbackQuery, state: FSMContext):

    message = callback.message

    await get_shedule_and_give_num(message, state, user_id=callback.from_user.id)

    await callback.answer()


@shedule_router.callback_query(GiveSchedule.slctnum and F.data.startswith('cls_'))
async def cb_cls_ikb(callback: CallbackQuery, state: FSMContext):

    cls_name = callback.data.split('_')[1]

    await state.update_data(selected_class_num=cls_name[:-1], selected_class_lit=cls_name[-1])
    res_text = f"📚 <b>Вы успешно выбрали класс {cls_name[:-1]} «{cls_name[-1]}» класс!</b>\n\n" \
               "🗓 Теперь выберите день, расписание которого вы хотите посмотреть 👇"

    await callback.message.answer(text=res_text, reply_markup=inline_kb.three_days_ikb())
    await callback.answer()
    await state.set_state(GiveSchedule.slct_day)


@shedule_router.message(GiveSchedule.slctnum)
async def give_lit(message: Message, state: FSMContext):
    if message.text:
        msg = message.text.strip()

        if message.text in ['5', '6', '7', '8', '9', '10', '11']:
            await state.set_state(GiveSchedule.slctlit)
            res_text = (f"📚 <b>Вы успешно выбрали номер класса {msg} «?» класс</b>\n\n"
                "<b>🔤 А давай выберем теперь литерал класса! Его также можно выбрать быстрее из кнопки под полем ввода\n\n"
                "<i>Либо напишите сами букву нужного для вас класса (любого регистра) 😉</i></b>")

            await state.update_data(selected_class_num=msg)

            await message.answer(text=res_text, reply_markup=await reply_kb.kb_select_class_lit())

        elif len(msg) > 1 and len(msg) < 4 and msg[:-1].isdigit() and 5 <= int(msg[:-1]) <= 11 and msg[-1].isalpha():

            await state.set_state(GiveSchedule.slctcls)
            selected_class_num = msg.upper()[:-1]
            selected_class_lit = msg.upper()[-1]

            res = res_cls = selected_class_num + selected_class_lit

            if res_cls in ['9А', '9Б', '5А', '5Б', '5П', '10А', '10Б', '11А', '11Б']:

                await state.update_data(selected_class_num=selected_class_num, selected_class_lit=selected_class_lit)
                res_text = f"📚 <b>Вы успешно выбрали класс {selected_class_num} «{selected_class_lit}» класс!</b>\n\n" \
                           "🗓 Теперь выберите день, расписание которого вы хотите посмотреть 👇"

                await message.answer(text=res_text, reply_markup=inline_kb.three_days_ikb())
                await state.set_state(GiveSchedule.slct_day)

            else:
                res_text = ("❌ <b>Данный класс не найден!</b>\n\n"
                            "🙏 Пожалуйста, введите корректный класс, который должен состоять из цифры (от 5 до 11) и одной буквы"
                            "<i> | Пример: '9А', '10Б', '11В' и т.д.</i>\n\n"
                            "Если класс все таки не отображается в списке, возможно, его расписание ещё не добавлено в базу данных.\n\n"
                            "<b>👇 Вы можете вернуться в меню, нажав на кнопку ниже или используйте команду - /menu</b>")
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEM_H9nE2X7FR6PqLJJXsw6rChl2eJusgAC6RMAAiBRQEtjB12ULYwTNjYE')
                await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())
                await state.set_state(GiveSchedule.slctnum)

        else:
            res_text = ("❌ <b>Неверный формат класса!</b>\n\n"
                        "🙏 Пожалуйста, введите номер класса, который должен состоять из цифры (от 5 до 11)\n"
                        "<i>Или сразу отправьте класс полного формата (например '9А', '10Б' и т.д.)</i>\n\n"
                        "<b>👇 Вы можете вернуться в меню, нажав на кнопку ниже или используйте команду - /menu</b>")

            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_AtnEq5NOXbSot3y4c-QRHar9YA4vgACfxEAAhhA8UrOIDTUp-mQxjYE')
            await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())


@shedule_router.message(GiveSchedule.slctlit)
async def slct_day(message: Message, state: FSMContext):
    if message.text:
        msg = message.text.upper()

        if msg not in ['А', 'Б', 'В', 'Ш', 'П'] and len(msg) == 1:
            res_text = ("❌ <b>Данный класс не найден!</b>\n\n"
                        "🙏 Пожалуйста, введите литерал класса, который может состоять из букв (А, Б, В, Ш, П)"
                        "<i> | Пример: 'А', 'Б', 'В' и т.д.</i>\n\n"
                        "Если класс все таки не отображается в списке, возможно, его расписание ещё не добавлено в базу данных.\n\n"
                        "<b>👇 Вы можете вернуться в меню, нажав на кнопку ниже или используйте команду - /menu</b>")
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_H9nE2X7FR6PqLJJXsw6rChl2eJusgAC6RMAAiBRQEtjB12ULYwTNjYE')
            await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())

        elif msg in ['А', 'Б', 'В', 'Ш', 'П'] and len(msg) == 1:
            data = await state.get_data()

            selected_class_num = data.get('selected_class_num')

            selected_class_lit = msg

            await state.update_data(selected_class_num=selected_class_num, selected_class_lit=selected_class_lit)

            res_cls = selected_class_num + selected_class_lit

            if res_cls in ['9А', '9Б', '5А', '5Б', '5П', '10А', '10Б', '11А', '11Б',
                           '6А', '6Ш', '7А', '7Б', '8А', '8Б', '8В']:

                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEM_CdnEsULTvJmtAxQchTdyV9IblWzoAACSEoAAvys-UtFgdP0svH3CDYE',
                    reply_markup=ReplyKeyboardRemove())
                class_info = f"<b>✅ Вы успешно выбрали {selected_class_num} «{selected_class_lit}» класс!</b>"

                await state.set_state(GiveSchedule.slct_day)

                await message.answer(f"{class_info}\n\n"
                                     f"🗓 А теперь пожалуйста, выберите день, расписание которого вы хотите посмотреть 👇",
                                     reply_markup=inline_kb.three_days_ikb())

            else:
                res_text = ("❌ <b>Данный класс не найден!</b>\n\n"
                            "🙏 Пожалуйста, перепроверьте литерал вашего класса и отправьте верный литерал"
                            "\nЕсли класс все таки не отображается в списке, "
                            "возможно, его расписание ещё не добавлено в базу данных.\n\n"
                            "<b>👇 Вы можете вернуться в меню, нажав на кнопку ниже или используйте команду - /menu</b>")
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEM_H9nE2X7FR6PqLJJXsw6rChl2eJusgAC6RMAAiBRQEtjB12ULYwTNjYE')
                await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())


        else:
            res_text = ("❌ <b>Неверный формат литерала (буква класса)!</b>\n\n"
                        "🙏 Пожалуйста, введите литерал класса, который может состоять из букв (А, Б, В, Ш, П)\n\n"
                        "<b>👇 Вы можете вернуться в меню, нажав на кнопку ниже или используйте команду - /menu</b>")

            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_AtnEq5NOXbSot3y4c-QRHar9YA4vgACfxEAAhhA8UrOIDTUp-mQxjYE')

            await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())


async def format_shedule(shedule_data: list):
    shedule = shedule_data

    lesson_numbers = [lesson['number'] for lesson in shedule]
    lesson_times = [lesson['time'] for lesson in shedule]
    lesson_subject = [lesson['subject'] for lesson in shedule]

    max_time_len = len(max(lesson_times, key=len))
    max_subject_len = len(max(lesson_subject, key=len))

    formatted_schedule = '<code>'

    for number, time, subject in zip(lesson_numbers, lesson_times, lesson_subject):
        formatted_schedule += f"{number}️⃣ | {time:<{max_time_len}} | {subject:<{max_subject_len}}\n"

    formatted_schedule += '</code>'

    return formatted_schedule


@shedule_router.callback_query(GiveSchedule.slct_day)
async def select_day_cb(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    selected_cls_num = data.get('selected_class_num')
    selected_cls_lit = data.get('selected_class_lit')

    days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Cуббота', 'Воскресенье']

    days_of_week_eng = ['pon', 'vtor', 'sred', 'chet', 'pyat']

    if callback.data == 'today':
        ind = datetime.today().weekday()
        today_name_rus = days_of_week[ind]

        if datetime.today().weekday() not in [5, 6]:

            select_day_name_eng = days_of_week_eng[datetime.today().weekday()]

            text = f"✅ Вот ваше расписание по запросу — <b>{today_name_rus} для {selected_cls_num} «{selected_cls_lit}» класса!</b>\n\n"

            full_cls = selected_cls_num + selected_cls_lit
            lessons = await Database.get_shedule_for_cls(full_cls)
            res_lessons = lessons[select_day_name_eng]

            if lessons:
                text += await format_shedule(res_lessons)

                await callback.message.edit_text(text=text, reply_markup=inline_kb.next_or_prev_day(full_cls, ind))

                await callback.answer(
                    text="😉 Спасибо, что воспользовались ботом!"
                )
                await state.set_state(GiveSchedule.waiting_next_or_prev)

        elif datetime.today().weekday() in [5, 6]:
            await callback.answer(
                    text=f"🌞 Сегодня {today_name_rus} — выходной! Отдыхай и набирайся сил 😉",
                    show_alert=True
            )

    elif callback.data == 'tomorrow':
        tomorrow_date = datetime.today() + timedelta(days=1)


        tomorrow_num = tomorrow_date.weekday()

        tomorrow_name_rus = days_of_week[tomorrow_num]

        if tomorrow_num not in [5, 6]:
            select_day_name_eng = days_of_week_eng[tomorrow_num]

            text = f"✅ Вот ваше расписание по запросу — <b>{tomorrow_name_rus} для {selected_cls_num} «{selected_cls_lit}» класса!</b>\n\n"

            full_cls = selected_cls_num + selected_cls_lit
            lessons = await Database.get_shedule_for_cls(full_cls)
            res_lessons = lessons[select_day_name_eng]

            if lessons:
                text += await format_shedule(res_lessons)

                sent_message = await callback.message.answer(text=".", reply_markup=ReplyKeyboardRemove())

                text += "<i>\nУдачного дня и отличных уроков! 💪📚</i>"

                await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sent_message.message_id)

                await state.set_state(GiveSchedule.waiting_next_or_prev)

                await callback.message.edit_text(text=text, reply_markup=inline_kb.next_or_prev_day(full_cls, tomorrow_num))

                await callback.answer(
                    text="😉 Спасибо, что воспользовались ботом!"
                )
                await state.set_state(GiveSchedule.waiting_next_or_prev)

        elif tomorrow_num in [5, 6]:
            await callback.answer(
                text=f"🌞 Завтра еще {tomorrow_name_rus} — выходной! Отдыхай и набирайся сил 😉",
                show_alert=True
            )

    elif callback.data == 'select_other':
        await callback.message.edit_text(
            text="<b>📅 Пожалуйста, выберите день недели, чтобы увидеть расписание</b>",
            reply_markup=inline_kb.other_days_ikb())
        await state.set_state(GiveSchedule.slct_other_day)
        await callback.answer()

    elif callback.data == 'menu':
        await state.clear()
        await cmd_menu(callback.message, state)
        await callback.answer()


@shedule_router.callback_query(GiveSchedule.slct_other_day)
async def select_other_day_cb(callback: CallbackQuery, state: FSMContext):
    if callback.data.split("_")[0] == 'day':
        data = await state.get_data()
        selected_cls_num = data.get('selected_class_num')
        selected_cls_lit = data.get('selected_class_lit')

        select_day_name_eng = callback.data.split('_')[-1]
        days_of_week_eng = ['pon', 'vtor', 'sred', 'chet', 'pyat']

        days_of_week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
        ind = days_of_week_eng.index(select_day_name_eng)
        select_day_name_rus = days_of_week[ind]

        text = f"✅ Вот ваше расписание по запросу — <b>{select_day_name_rus} для {selected_cls_num} «{selected_cls_lit}» класса!</b>\n\n"
        full_cls = selected_cls_num + selected_cls_lit
        lessons = await Database.get_shedule_for_cls(full_cls)

        if lessons:
            res_lessons = lessons[select_day_name_eng]
            text += await format_shedule(res_lessons)

        else:
            text += "Уроки не найдены для этого дня."

        text += "<i>\nУдачного дня и отличных уроков! 💪📚</i>"

        sent_message = await callback.message.answer(text=".", reply_markup=ReplyKeyboardRemove())
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=sent_message.message_id)

        await callback.message.edit_text(text=text, reply_markup=inline_kb.next_or_prev_day(full_cls, ind))

        await callback.answer(
                text="😉 Спасибо, что воспользовались ботом!"
            )
        await state.set_state(GiveSchedule.waiting_next_or_prev)

    elif callback.data == 'menu':
        await state.clear()
        await cmd_menu(callback.message, state)
        await callback.answer()


@shedule_router.callback_query(GiveSchedule.waiting_next_or_prev)
async def next_or_prev_cb(callback: CallbackQuery, state: FSMContext):

    data_split = callback.data.split('_')

    if len(data_split) == 3:
        a, cls_name_rus, day_index = callback.data.split('_')

        days_of_week_eng = ['pon', 'vtor', 'sred', 'chet', 'pyat']
        days_of_week_rus = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']

        if a == 'prev':
            prev_day_index = (int(day_index) - 1) % len(days_of_week_eng)
            day_name_eng = days_of_week_eng[prev_day_index]
            day_name_rus = days_of_week_rus[prev_day_index]

            text = f"✅ Вот ваше расписание по запросу — <b>{day_name_rus} для {cls_name_rus[:-1]} «{cls_name_rus[-1]}» класса!</b>\n\n"
            full_cls = cls_name_rus
            lessons = await Database.get_shedule_for_cls(full_cls)
            res_lessons = lessons[day_name_eng]

            if lessons:
                text += await format_shedule(res_lessons)

            else:
                text += "Уроки не найдены для этого дня."

            text += "<i>\nУдачного дня и отличных уроков! 💪📚</i>"

            await callback.message.edit_text(text=text, reply_markup=inline_kb.next_or_prev_day(full_cls, prev_day_index))

        elif a == 'next':
            next_day_index = (int(day_index) + 1) % len(days_of_week_eng)
            day_name_eng = days_of_week_eng[next_day_index]
            day_name_rus = days_of_week_rus[next_day_index]

            text = f"✅ Вот ваше расписание по запросу — <b>{day_name_rus} для {cls_name_rus[:-1]} «{cls_name_rus[-1]}» класса!</b>\n\n"
            full_cls = cls_name_rus
            lessons = await Database.get_shedule_for_cls(full_cls)
            res_lessons = lessons[day_name_eng]

            if lessons:
                text += await format_shedule(res_lessons)

            else:
                text += "Уроки не найдены для этого дня."

            text += "<i>\nУдачного дня и отличных уроков! 💪📚</i>"

            await callback.message.edit_text(text=text, reply_markup=inline_kb.next_or_prev_day(full_cls, next_day_index))
