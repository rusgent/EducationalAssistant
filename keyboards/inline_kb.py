from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           KeyboardButtonPollType)

from aiogram.utils.keyboard import InlineKeyboardBuilder


def q1_ikb():
    buttons = [
        [InlineKeyboardButton(text="👥 Работать с людьми", callback_data="q1_human"),
         InlineKeyboardButton(text="🔧 Работать с техникой", callback_data="q1_tech")],
        [InlineKeyboardButton(text="🗂️ Работать с информацией", callback_data="q1_info")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=buttons)


def q2_ikb():
    buttons = [
        [InlineKeyboardButton(text="📊 Анализировать данные", callback_data="q2_analyze"),
         InlineKeyboardButton(text="🛠️ Создавать что-то новое", callback_data="q2_create")],
        [InlineKeyboardButton(text="💬 Общаться с людьми", callback_data="q2_communicate")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=buttons)


def q3_ikb():
    buttons = [
        [InlineKeyboardButton(text="🔬 Научные исследования", callback_data="q3_research"),
         InlineKeyboardButton(text="🎨 Творчество и искусство", callback_data="q3_art")],
        [InlineKeyboardButton(text="⚙️ Техническое обеспечение", callback_data="q3_tech")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=buttons)


def calculate_result(data):

    scores = {
        "Гуманитарий": 0,
        "Технарь": 0,
        "Аналитик": 0,
        "Творец": 0,
    }

    if data['answer1'] == "human":
        scores["Гуманитарий"] += 1
    elif data['answer1'] == "tech":
        scores["Технарь"] += 1
    elif data['answer1'] == "info":
        scores["Аналитик"] += 1
    
    if data['answer2'] == "analyze":
        scores["Аналитик"] += 1
    elif data['answer2'] == "create":
        scores["Творец"] += 1
    elif data['answer2'] == "communicate":
        scores["Гуманитарий"] += 1

    if data['answer3'] == "research":
        scores["Аналитик"] += 1
    elif data['answer3'] == "art":
        scores["Творец"] += 1
    elif data['answer3'] == "tech":
        scores["Технарь"] += 1

    result = max(scores, key=scores.get)
    return result


def share_ikb():
    button = [
        [InlineKeyboardButton(text="🔗 Поделиться результатом", callback_data="share_result")]]
    
    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=button)


def menu_ikb():
    button = [
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]]

    return InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=button)


def three_days_ikb():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(text="🗓 Сегодня", callback_data="today"),
            InlineKeyboardButton(text="📅 Завтра", callback_data="tomorrow"),
        ],
        [
            InlineKeyboardButton(text="🔄 Выбрать другой день", callback_data="select_other"),
            InlineKeyboardButton(text="🚪 Меню", callback_data="menu")
        ],
    ])

    return keyboard


def other_days_ikb():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [
            InlineKeyboardButton(text="Понедельник", callback_data="day_pon"),
            InlineKeyboardButton(text="Вторник", callback_data="day_vtor"),
        ],
        [
            InlineKeyboardButton(text="Среда", callback_data="day_sred"),
            InlineKeyboardButton(text="Четверг", callback_data="day_chet")
        ],
        [
            InlineKeyboardButton(text="Пятница", callback_data="day_pyat"),
            InlineKeyboardButton(text="🚪 Меню", callback_data="menu")
        ],
    ])

    return keyboard


def get_menu_ikb():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="🗃 Расписание", callback_data="schedule")],
        [InlineKeyboardButton(text="🧠 Тест на профориентацию", callback_data="test")],
        [InlineKeyboardButton(text="🧮 Калькулятор оценок", callback_data="calc_marks")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="📋 Трекер задач", callback_data="todo")],
        [InlineKeyboardButton(text="🍴 Меню столовой", callback_data="school_menu")]
        ]
        )

    return keyboard


def get_new_shedule():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="🗃 Получить новое расписание", callback_data="new_schedule")]])

    return keyboard


def get_del_or_add_favcls_or_menu():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить класс", callback_data="del_cls")],
        [InlineKeyboardButton(text="➕ Добавить класс", callback_data="add_cls")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]])

    return keyboard


def get_only_menu():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]])

    return keyboard


def get_favcls_ikb(favcls_list):
    ikb = InlineKeyboardBuilder()

    for cls in favcls_list:
        ikb.button(text=f'{cls}', callback_data=f'cls_{cls}')

    ikb.adjust(3)

    return ikb.as_markup(resize_keyboard=True)


def get_delfavcls_ikb(favcls_list):
    ikb = InlineKeyboardBuilder()

    for cls in favcls_list:
        ikb.button(text=f'{cls}', callback_data=f'delcls_{cls}')

    ikb.adjust(3)

    return ikb.as_markup(resize_keyboard=True)


def get_yes_or_no_ikb():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="✅ Знаю", callback_data='yes')],
        [InlineKeyboardButton(text="🙁 Не знаю", callback_data='no')]])

    return ikb


def three_four_five_marks():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="3", callback_data='3'),
         InlineKeyboardButton(text="4", callback_data='4'),
         InlineKeyboardButton(text="5", callback_data='5')],
        [InlineKeyboardButton(text="3.5", callback_data='3.5'),
         InlineKeyboardButton(text="4.5", callback_data='4.5')]
    ])

    return ikb


def list_2345_marks():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="2", callback_data='2'),
         InlineKeyboardButton(text="3", callback_data='3'),
         InlineKeyboardButton(text="4", callback_data='4'),
         InlineKeyboardButton(text="5", callback_data='5')],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ])

    return ikb


def next_or_prev_day(cls, ind_day):
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data=f'prev_{cls}_{ind_day}'),
         InlineKeyboardButton(text="➡️", callback_data=f'next_{cls}_{ind_day}')],
        [InlineKeyboardButton(text="🗃 Получить новое расписание", callback_data="new_schedule")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ])

    return ikb


def get_todo_ikb():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="📋 Просмотр задач", callback_data="view_tasks")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ])

    return ikb


def get_view_tasks_ikb():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить новую задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="📋 Просмотр задач", callback_data="view_tasks")],
        [InlineKeyboardButton(text="🚪 Меню", callback_data="menu")]
    ])

    return ikb


def get_tasks_list(tasks,page=0, tasks_per_page=5):
    ikb = InlineKeyboardBuilder()
    
    start = page * tasks_per_page
    end = start + tasks_per_page
    tasks_on_page = tasks[start:end]
    
    for task in tasks_on_page:
        ikb.button(text=task.task_name, callback_data=f'task_{task.id}')
    
    count_nav_buttons = 0
    if page > 0:
        ikb.button(text="⬅️", callback_data=f'tprev_{page-1}')
        count_nav_buttons += 1
        
    if end < len(tasks):
        ikb.button(text="➡️", callback_data=f'tprev_{page+1}')
        count_nav_buttons += 1
    
    ikb.button(text="🚪 Меню", callback_data="menu")

    task_count = len(tasks_on_page)

    if count_nav_buttons > 0:
        ikb.adjust(*([1] * task_count), count_nav_buttons, 1)
    else:
        ikb.adjust(*([1] * task_count), 1)

    return ikb.as_markup(resize_keyboard=True)


def get_func_task_ikb(task_id: int):
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data=f"finish_task_{task_id}")],
        [InlineKeyboardButton(text="✍ Изменить данные", callback_data=f"edit_task_{task_id}")],
        [InlineKeyboardButton(text="🗑 Удалить задачу", callback_data=f"del_task_{task_id}")],
        [InlineKeyboardButton(text="🚪 Назад", callback_data=f"view_tasks_{task_id}")]
    ])

    return ikb


def get_func_edit_task_ikb(task_id: int):
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="Изменить название", callback_data=f"edit_taskname_{task_id}")],
        [InlineKeyboardButton(text="Изменить описание", callback_data=f"edit_taskdescription_{task_id}")],
        [InlineKeyboardButton(text="◀ Вернуться к задаче", callback_data=f"back_{task_id}")]
    ])

    return ikb


def get_func_back_to_task(task_id: int):
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="◀ Вернуться к задаче", callback_data=f"back_{task_id}")]
    ])

    return ikb


def get_yes_or_no(task_id: int):
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Да", callback_data=f"yes_{task_id}"),
        InlineKeyboardButton(text="🔴 Нет", callback_data=f"no_{task_id}")]
    ])
    
    return ikb

def exit_to_register_task():
    ikb = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отменить", callback_data=f"exit_to_reg")]
    ])
    
    return ikb

def get_vkl_menu():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="✅ Включить", callback_data="school_menu_vkl")]])

    return keyboard

def get_otkl_menu():
    keyboard = InlineKeyboardMarkup(resize_keyboard=True, inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отключить", callback_data="school_menu_otkl")]])

    return keyboard