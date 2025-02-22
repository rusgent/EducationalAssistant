from aiogram.fsm.state import State, StatesGroup


class NewsStates(StatesGroup):
    title = State()
    content = State()
    image = State()


class CreateGroupStates(StatesGroup):
    group_name = State()


class StartStates(StatesGroup):
    group_name = State()


class TestStates(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()


class GiveSchedule(StatesGroup):
    slctnum = State()
    slctlit = State()
    slctcls = State()

    slct_day = State()
    slct_other_day = State()

    waiting_next_or_prev = State()


class FavCls(StatesGroup):
    slctnum = State()
    slctlit = State()
    slctcls = State()
    delcls = State()
    none_list = State()


class MarksState(StatesGroup):
    waiting_yes_or_no = State()
    waiting_middle_mark = State()
    waiting_list_marks = State()
    waiting_target_mark = State()
    
    waiting_add_marks = State()


class Task(StatesGroup):
    add_name_newtask = State()
    add_desc_newtask = State()
    
    edit_name_task = State()
    edit_desc_task = State()
    

class SendMenu(StatesGroup):
    wait_photo = State()
    wait_yes = State()
    
