from aiogram import Router
from aiogram import F, Router, Bot
from aiogram.filters import Command
from .states import Task
from keyboards import inline_kb
from aiogram.fsm.context import FSMContext
from database.orm import Database
from handlers.user_routers.texts import *
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

todo_router = Router()


@todo_router.callback_query(F.data == 'add_task')
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=TODO_ADD_TASK_GIVE_NAME_TASK)
    await state.set_state(Task.add_name_newtask)
    await callback.answer()

@todo_router.message(Task.add_name_newtask)
async def give_name_task(message: Message, state: FSMContext):
    if message.text:
        task_name = message.text
        await state.update_data(task_name=task_name)
        await message.answer(text=TODO_NICE_NAME_TASK_GIVE_DESC_TASK.format(task_name=task_name))
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
        
        
        

@todo_router.callback_query(F.data == 'view_tasks')
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    TEXT = (f"📋 <b>Просмотр задач</b>\n\n"
             "👇 Выбери ниже кнопку задачи, чтобы посмотреть ее подробности и взаимодействовать с ней")

    tasks = await Database.get_tasks_list(user_id=callback.from_user.id)
    await state.update_data(tasks=tasks)
    
    ikb = inline_kb.get_tasks_list(tasks, 0)
    
    await callback.message.edit_text(text=TEXT, reply_markup=ikb)
    await callback.answer()
    
    
@todo_router.callback_query(F.data.startswith('tprev') | F.data.startswith('tnext'))
async def next_or_prev_tasks_list(callback: CallbackQuery, state: FSMContext):
    _, page = callback.data.split('_')
    page = int(page)

    data = await state.get_data()
    tasks = data.get('tasks')
    
    ikb = inline_kb.get_tasks_list(tasks, page=page)
    
    await callback.message.edit_reply_markup(reply_markup=ikb)
    await callback.answer()
    

@todo_router.callback_query(F.data.startswith('task_'))
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[1])

    task = await Database.get_task(task_id=task_id)

    
    TEXT = (f'Ваша задача\n'
            f'<b>Название - <i>{task.task_name}</i></b>\n'
            f'<b>Описание - <i>{task.description}</i></b>\n'
            f'<b>Статус - <i>{task.status}</i></b>')

    
    await callback.message.edit_text(text=TEXT, reply_markup=inline_kb.get_func_task_ikb())
    await callback.answer()





