from aiogram.fsm.state import State, StatesGroup

class AddNewPrem(StatesGroup):
    wait_send_id = State()
    wait_send_money = State()
    
class DelPrem(StatesGroup):
    wait_send_id = State()
    wait_send_money = State()
