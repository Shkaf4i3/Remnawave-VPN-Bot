from aiogram.fsm.state import State, StatesGroup


class Balance(StatesGroup):
    amount = State()


class Mailing(StatesGroup):
    mailing_message = State()


class User(StatesGroup):
    tg_id = State()
