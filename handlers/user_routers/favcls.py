from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from .common import *
from database.orm import Database
from handlers.user_routers.states import FavCls
from keyboards import inline_kb, reply_kb

favcls_router = Router()


@favcls_router.callback_query(F.data == 'del_cls')
async def cb_del_favcls(callback: CallbackQuery, state: FSMContext):

    await state.set_state(FavCls.delcls)

    user_id = callback.from_user.id

    favcls_list = await Database.get_favcls_list(user_id)

    if len(favcls_list) > 0:

        text = (
                "<b>🗳 Чтобы удалить класс из избранных, выберите его ниже</b> — "
                "<i>нажмите на соответствующую кнопку под данным сообщения</i> 👇")

        await callback.message.answer(text=text,
                                      parse_mode='HTML',
                                      reply_markup=inline_kb.get_delfavcls_ikb(favcls_list))
        await callback.answer()

    else:

        await callback.answer(text='❌ У вас еще нету избранных классов!', show_alert=True)


@favcls_router.callback_query(F.data == 'add_cls')
async def cb_add_favcls(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FavCls.slctnum)
    text = (
            "<b>🗳 Чтобы добавить класс в избранные, введите номер класса</b> — "
            "<i>нажмите на соответствующую кнопку под полем ввода или введите номер класса вручную"
            "(например, 9A или 10А)</i>\n\n")

    await callback.message.answer(text=text,
                                  parse_mode='HTML',
                                  reply_markup=await reply_kb.kb_select_class_num())
    await callback.answer()


@favcls_router.message(FavCls.slctnum)
async def give_lit_favcls(message: Message, state: FSMContext):
    if message.text:
        msg = message.text.strip()

        if message.text in ['5', '6', '7', '8', '9', '10', '11']:
            await state.set_state(FavCls.slctlit)
            await state.update_data(selected_class_num=msg)

            await message.answer(text=FAVCLS_NICE_NUMBER.format(msg=msg), reply_markup=await reply_kb.kb_select_class_lit())


        elif len(msg) > 1 and len(msg) < 4 and msg[:-1].isdigit() and 5 <= int(msg[:-1]) <= 11 and msg[-1].isalpha():

            selected_class_num = msg.upper()[:-1]
            selected_class_lit = msg.upper()[-1]

            res = res_cls = selected_class_num + selected_class_lit

            if res_cls in ['9А', '9Б', '5А', '5Б', '5П', '10А', '10Б', '11А', '11Б']:

                await state.update_data(selected_class_num=selected_class_num, selected_class_lit=selected_class_lit)

                favcls_list = await Database.get_favcls_list(message.from_user.id)

                if res_cls not in favcls_list:

                    await Database.set_favcls(message.from_user.id, res_cls)
                    res_text = f"📚 <b>Вы успешно добавили {selected_class_num} «{selected_class_lit}» класс в избранные!</b>\n\n" \
                               "😁<b>Просмотреть свои избранные классы можете получив расписание</b>"

                    await message.answer(text=res_text, reply_markup=inline_kb.get_new_shedule())
                    await state.clear()

                else:

                    await message.reply(f'🚫 Данный класс уже есть в ваших избранных!')

            else:
                await message.answer_sticker(
                    sticker='CAACAgIAAxkBAAEM_H9nE2X7FR6PqLJJXsw6rChl2eJusgAC6RMAAiBRQEtjB12ULYwTNjYE')
                await message.answer(text=FAVLCS_NOT_FIND_CLASS,
                                 reply_markup=inline_kb.menu_ikb())
                await state.set_state(FavCls.slctnum)

        else:
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_AtnEq5NOXbSot3y4c-QRHar9YA4vgACfxEAAhhA8UrOIDTUp-mQxjYE')
            await message.answer(text=FAVLCS_ERROR_FORMAT_CLASS,
                                 reply_markup=inline_kb.menu_ikb())


@favcls_router.message(FavCls.slctlit)
async def slct_day_favcls(message: Message, state: FSMContext):
    if message.text:
        msg = message.text.upper()

        if msg not in ['А', 'Б', 'В', 'Ш', 'П'] and len(msg) == 1:
            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_H9nE2X7FR6PqLJJXsw6rChl2eJusgAC6RMAAiBRQEtjB12ULYwTNjYE')
            await message.answer(text=FAVCLS_ERROR_NOT_FIND_CLASS_GIVE_LIT,
                                 reply_markup=inline_kb.menu_ikb())

        elif msg in ['А', 'Б', 'В', 'Ш', 'П'] and len(msg) == 1:
            data = await state.get_data()

            selected_class_num = data.get('selected_class_num')
            selected_class_lit = msg

            await state.update_data(selected_class_num=selected_class_num, selected_class_lit=selected_class_lit)

            res_cls = selected_class_num + selected_class_lit

            if res_cls in ['9А', '9Б', '5А', '5Б', '5П', '10А', '10Б', '11А', '11Б']:

                favcls_list = await Database.get_favcls_list(message.from_user.id)

                if res_cls not in favcls_list:

                    await Database.set_favcls(message.from_user.id, res_cls)
                    await message.answer_sticker(
                        sticker='CAACAgIAAxkBAAEM_CdnEsULTvJmtAxQchTdyV9IblWzoAACSEoAAvys-UtFgdP0svH3CDYE',
                        reply_markup=ReplyKeyboardRemove())

                    class_info = (
                        f"<b>✅ Вы успешно добавили {selected_class_num} «{selected_class_lit}» класс в избранные!</b>\n"
                        f"😁<b>Просмотреть свои избранные классы можете получив расписание</b>")

                    await state.clear()

                    await message.answer(f"{class_info}",
                                         reply_markup=inline_kb.get_new_shedule())

                else:

                    await message.reply(f'🚫 Данный класс уже есть в ваших избранных!')

        else:
            res_text = ("❌ <b>Неверный формат литерала (буква класса)!</b>\n\n"
                        "🙏 Пожалуйста, введите литерал класса, который может состоять из букв (А, Б, В, Ш, П)\n\n")

            await message.answer_sticker(
                sticker='CAACAgIAAxkBAAEM_AtnEq5NOXbSot3y4c-QRHar9YA4vgACfxEAAhhA8UrOIDTUp-mQxjYE')

            await message.answer(text=res_text,
                                 reply_markup=inline_kb.menu_ikb())


@favcls_router.callback_query(F.data.startswith('delcls_'), FavCls.delcls)
async def cb_set_del_favcls(callback: CallbackQuery):
    delcls = callback.data.split('_')[1]

    delete_cls = await Database.del_favcls(callback.from_user.id, delcls)

    if delete_cls:
        await callback.answer(text='🗑 Данный класс был успешно удален!', show_alert=True)
        remove_delfavcls_list = await Database.get_favcls_list(callback.from_user.id)
        if not remove_delfavcls_list:
            await callback.message.edit_text(text='<b>😔 У вас больше не осталось избранных классов\n\n'
                                                  '🗂 Чтобы добавить класс -> /favorites</b>')
        else:
            await callback.message.edit_reply_markup(reply_markup=inline_kb.get_delfavcls_ikb(remove_delfavcls_list))
    else:
        await callback.answer(text='ERROR :(', show_alert=True)
