from aiogram import Router
from aiogram import F, Router, Bot
from aiogram.filters import Command
from .states import Task
from keyboards import inline_kb
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from database.orm import Database
from .common import *
from handlers.user_routers.texts import *
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

todo_router = Router()


@todo_router.callback_query(F.data == 'todo')
async def cb_todo_menu(callback: CallbackQuery, state: FSMContext):
    sent_message = await callback.message.answer_sticker(sticker="CAACAgIAAxkBAAENXKZnZb7qQc48z8cCp6jlLOVZo8WznQACQQEAAs0bMAjx8GIY3_aWWDYE", reply_markup=ReplyKeyboardRemove())
    await callback.message.bot.delete_message(chat_id=callback.message.chat.id, message_id=sent_message.message_id)
    
    await state.clear()

    await callback.message.answer(text=TEXT_INFO_TREKER, reply_markup=inline_kb.get_todo_ikb())

    await callback.answer()

@todo_router.callback_query(F.data == 'add_task')
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text=TODO_ADD_TASK_GIVE_NAME_TASK, reply_markup=inline_kb.exit_to_register_task())
    await state.set_state(Task.add_name_newtask)
    await callback.answer()


@todo_router.message(Task.add_name_newtask)
async def give_name_task(message: Message, state: FSMContext):
    if message.text:
        task_name = message.text
        await state.update_data(task_name=task_name)
        await message.answer(text=TODO_NICE_NAME_TASK_GIVE_DESC_TASK.format(task_name=task_name),reply_markup=inline_kb.exit_to_register_task())
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
            f"✅ <b>Задача была успешно добавлена!</b>\n\n"
            f"<blockquote><b>Название задачи:</b> {task_name}\n"
            f"<b>Описание:</b> {desc_task}</blockquote>\n\n"
        )

        await message.answer(TEXT, reply_markup=inline_kb.get_view_tasks_ikb())
        
        await state.clear()

    else:
        await message.answer(
            text="❌ Описание задачи может быть только <b>ТЕКСТОМ</b>"
        )
        
        
@todo_router.callback_query(F.data == 'exit_to_reg', StateFilter(Task.add_desc_newtask, Task.add_name_newtask))
async def exit_to_register_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    
    await state.clear()

    await callback.message.answer(text=TEXT_INFO_TREKER, reply_markup=inline_kb.get_todo_ikb())
    await callback.answer()

@todo_router.callback_query(F.data.startswith('view_tasks'))
async def view_task(callback: CallbackQuery, state: FSMContext):
    tasks = await Database.get_tasks_list(user_id=callback.from_user.id)
    
    if tasks:
        TEXT = (f"📋 <b>Просмотр задач</b>\n\n"
                "👇 Выбери ниже кнопку задачи, чтобы посмотреть ее подробности и взаимодействовать с ней")
        await state.update_data(tasks=tasks)
        
        ikb = inline_kb.get_tasks_list(tasks, 0)
        
        await callback.message.edit_text(text=TEXT, reply_markup=ikb)
        await callback.answer()
        
    else:
        TEXT = 'У вас нет поставленных задач ☹'
        await callback.answer(text=TEXT, show_alert=True)
    
    
@todo_router.callback_query(F.data.startswith('tprev') | F.data.startswith('tnext'))
async def next_or_prev_tasks_list(callback: CallbackQuery, state: FSMContext):
    _, page = callback.data.split('_')
    page = int(page)

    data = await state.get_data()
    tasks = data.get('tasks')
    
    ikb = inline_kb.get_tasks_list(tasks, page=page)
    
    await callback.message.edit_reply_markup(reply_markup=ikb)
    await callback.answer()
    

@todo_router.callback_query(F.data.startswith('task_') | F.data.startswith('back_'))
async def cb_add_task(callback: CallbackQuery, state: FSMContext):
    
    task_id = int(callback.data.split('_')[1])
    
    task = await Database.get_task(task_id=task_id)
    await state.update_data(task=task)

    
    TEXT = (
            f'<blockquote><b>Название - <i>{task.task_name}</i></b>\n'
            f'<b>Описание - <i>{task.description}</i></b>\n'
            f'<b>Статус - <i>{task.status}</i></b></blockquote>')

    
    await callback.message.edit_text(text=TEXT, reply_markup=inline_kb.get_func_task_ikb(task_id))
    await callback.answer()
    
    
@todo_router.callback_query(F.data.startswith('edit_task_'))
async def edit_task(callback: CallbackQuery):
    a, b, task_id = callback.data.split('_')
    
    if task_id:
        await callback.message.edit_reply_markup(reply_markup=inline_kb.get_func_edit_task_ikb(task_id=task_id))
        

@todo_router.callback_query(F.data.startswith('edit_task'))
async def edit_func_task(callback: CallbackQuery, state: FSMContext):
    _, func, task_id = callback.data.split('_')
    
    task = await Database.get_task(task_id=task_id)
    await state.update_data(task=task)
    
    if func == 'taskname':
        
        await state.set_state(Task.edit_name_task)
        await callback.message.edit_text(text=TODO_EDIT_TASK_GIVE_NAME_TASK.format(
            task_name=task.task_name,
            description=task.description,
            status=task.status
        ), reply_markup=inline_kb.get_func_back_to_task(task.id))
        
    elif func == 'taskdescription':
        
        await state.set_state(Task.edit_desc_task)
        await callback.message.edit_text(text=TODO_EDIT_TASK_GIVE_DESC_TASK.format(
            task_name=task.task_name,
            description=task.description,
            status=task.status
        ), reply_markup=inline_kb.get_func_back_to_task(task.id))
        
@todo_router.message(Task.edit_name_task)
async def edit_task_name(message: Message, state: FSMContext):

    if message.text:

        data = await state.get_data()
        task = data.get('task')
        
        new_task_name = message.text
        upd_task = await Database.edit_task_name(task_id=task.id, new_task_name=new_task_name)
        
        TEXT = (f'<b>✅ Название задачи успешно изменено!</b>\n\n'
        f'<blockquote><b>Название - <i>{upd_task.task_name}</i></b>\n'
        f'<b>Описание - <i>{upd_task.description}</i></b>\n'
        f'<b>Статус - <i>{upd_task.status}</i></b></blockquote>')
        
        await message.answer(text=TEXT, reply_markup=inline_kb.get_func_task_ikb(upd_task.id))
        await state.clear()

    else:
        await message.answer(
            text="❌ Название задачи может быть только <b>ТЕКСТОМ</b>"
        )


@todo_router.message(Task.edit_desc_task)
async def edit_task_desc(message: Message, state: FSMContext):

    if message.text:
        data = await state.get_data()
        task = data.get('task')
        
        new_task_desc = message.text
        upd_task = await Database.edit_task_desc(task_id=task.id, new_task_desc=new_task_desc)
        
        TEXT = (f'<b>✅ Описание задачи успешно изменено!</b>\n\n'
        f'<blockquote><b>Название - <i>{upd_task.task_name}</i></b>\n'
        f'<b>Описание - <i>{upd_task.description}</i></b>\n'
        f'<b>Статус - <i>{upd_task.status}</i></b></blockquote>')
        
        await message.answer(text=TEXT, reply_markup=inline_kb.get_func_task_ikb(upd_task.id))
        await state.clear()

    else:
        await message.answer(
            text="❌ Описание задачи может быть только <b>ТЕКСТОМ</b>"
        )
      
        
@todo_router.callback_query(F.data.startswith('del_task_'))
async def del_yes_or_no_task(callback: CallbackQuery):
    a, b, task_id = callback.data.split('_')
    TEXT=('<b>Вы точно хотите удалить задачу ❔</b>')
    await callback.message.edit_text(text=TEXT, reply_markup=inline_kb.get_yes_or_no(task_id=task_id))


@todo_router.callback_query(F.data.startswith('yes_'))
async def yes_del_task(callback: CallbackQuery, state: FSMContext):
    _, task_id = callback.data.split('_')
    task_del = await Database.del_task(task_id=task_id)
    if task_del:
    
        TEXT = (f'🗑Задача успешно была удалена!')
        
        await callback.answer(text=TEXT, show_alert=True)
        
        tasks = await Database.get_tasks_list(user_id=callback.from_user.id)
    
        if tasks:
            TEXT = (f"📋 <b>Просмотр задач</b>\n\n"
                    "👇 Выбери ниже кнопку задачи, чтобы посмотреть ее подробности и взаимодействовать с ней")
            await state.update_data(tasks=tasks)
            
            ikb = inline_kb.get_tasks_list(tasks, 0)
            
            await callback.message.edit_text(text=TEXT, reply_markup=ikb)
            await callback.answer()
            
        else:
            await cmd_todo(callback.message, state)
        
        
@todo_router.callback_query(F.data.startswith('no_'))
async def no_del_task(callback: CallbackQuery, state: FSMContext):
    _, task_id = callback.data.split('_')
    
    task = await Database.get_task(task_id=task_id)
    await state.update_data(task=task)

    TEXT = (f'Ваша задача\n'
            f'<blockquote><b>Название - <i>{task.task_name}</i></b>\n'
            f'<b>Описание - <i>{task.description}</i></b>\n'
            f'<b>Статус - <i>{task.status}</i></b></blockquote>')

    
    await callback.message.edit_text(text=TEXT, reply_markup=inline_kb.get_func_task_ikb(task_id))
    await callback.answer()
    

@todo_router.callback_query(F.data.startswith('finish_task_'))
async def finish_task(callback: CallbackQuery, state: FSMContext):
    task_id = callback.data.split('_')[2]
    responce = await Database.del_task(task_id)
    if responce:
        await callback.answer(text=('C успешным выполнением задачи 🥳\n'
                                    'Продолжай в том духе духе!'), show_alert=True)
        tasks = await Database.get_tasks_list(user_id=callback.from_user.id)
    
        if tasks:
            TEXT = (f"📋 <b>Просмотр задач</b>\n\n"
                    "👇 Выбери ниже кнопку задачи, чтобы посмотреть ее подробности и взаимодействовать с ней")
            await state.update_data(tasks=tasks)
            
            ikb = inline_kb.get_tasks_list(tasks, 0)
            
            await callback.message.edit_text(text=TEXT, reply_markup=ikb)
            await callback.answer()
            
        else:
            await cmd_todo(callback.message, state)
        
        
        
        
        
        





