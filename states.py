from aiogram.fsm.state import State, StatesGroup

class FeedbackSG(StatesGroup):
    waiting_rating = State()
    waiting_comment = State()

class BookingSG(StatesGroup):
    waiting_date = State()
    waiting_time = State()
    waiting_guests = State()
    waiting_wishes = State()
    waiting_phone = State()
