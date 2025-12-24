from aiogram.fsm.state import State, StatesGroup

class TicketState(StatesGroup):
    text = State()
    photo = State()

class AdminAnswerState(StatesGroup):
    ticket_id = State()
    message = State()