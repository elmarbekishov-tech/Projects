from aiogram.fsm.state import State, StatesGroup

class RegisterState(StatesGroup):
    name = State()
    group = State()
    phone = State()
    confirm = State()