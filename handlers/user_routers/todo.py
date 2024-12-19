from aiogram import Router
from aiogram import F, Router, Bot
from aiogram.filters import Command
from .states import Task
from keyboards import inline_kb
from aiogram.fsm.context import FSMContext
from database.orm import Database
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

todo_router = Router()


@todo_router.message(Command('todo'))
async def cmd_todo(message: Message):
    TEXT = (f"📝 <b>Трекер задач</b>\n\n"
    "Здесь ты можешь легко управлять своими задачами: добавлять, просматривать и удалять их.\n"
    "Я могу напоминать тебе о важных задачах, следить за сроками и помогать не забывать о важных делах!\n\n"
    "✨ <i>Выбери действие ниже и начни работать над задачами!</i>"
    )

    await message.answer(text=TEXT, reply_markup=inline_kb.get_todo_ikb())


@todo_router.callback_query(F.data == 'add_task')
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    TEXT = (f"➕ <b>Добавление новой задачи</b>\n\n"
        "🚀 Отлично, давай начнем! Для того чтобы я мог добавить твою задачу, "
        "напиши мне <b>название задачи</b>, чтобы мы могли двигаться дальше.\n")

    await callback.message.answer(text=TEXT)
    await state.set_state(Task.add_name_newtask)
    await callback.answer()


@todo_router.callback_query(F.data == 'view_tasks')
async def cb_add_task(callback: CallbackQuery):
    TEXT = (f"📋 <b>Просмотр задач</b>\n\n"
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! "
            "напиши мне <b>название задачи</b>, чтобы мы могли двигаться дальше.\n")

    await callback.message.answer(text=TEXT)
    await callback.answer()


@todo_router.message(Task.add_name_newtask)
async def give_name_task(message: Message, state: FSMContext):
    if message.text:
        task_name = message.text
        await state.update_data(task_name=task_name)
        TEXT = (
            f"<blockquote><b>Название задачи:</b> {task_name}\n"
            f"<b>Описание:</b> ???</blockquote>\n\n"
            "🎉 Отлично, название задачи добавлено!\n"
            "Теперь, чтобы завершить создание задачи, отправь мне <b>описание</b> или <b>суть</b> задачи"
        )

        await message.answer(text=TEXT)
        await state.set_state(Task.add_desc_newtask)

    else:
        await message.answer(
            text="❌ Название задачи может быть только <b>ТЕКСТОМ</b>"
        )


@todo_router.message(Task.add_desc_newtask)
async def give_desc_task(message: Message, state: FSMContext):
    if message.text:
        desc_task = message.text
        await state.update_data(desc_task=desc_task)

        data = await state.get_data()
        task_name = data.get('task_name')
        desc_task = data.get('desc_task')

        await Database.set_task(message.from_user.id,
                                task_name, desc_task)

        TEXT = (
            f"<blockquote><b>Название задачи:</b> {task_name}\n"
            f"<b>Описание:</b> {desc_task}</blockquote>\n\n"
            f"✅ <b>Задача была успешно добавлена!</b>"
        )

        await message.answer(TEXT, reply_markup=inline_kb.get_view_tasks_ikb())

    else:
        await message.answer(
            text="❌ Описание задачи может быть только <b>ТЕКСТОМ</b>"
        )




