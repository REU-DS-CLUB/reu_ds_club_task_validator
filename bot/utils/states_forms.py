from aiogram.fsm.state import StatesGroup, State


class StartStep(StatesGroup):
    MAIN = State()


class ProfileStep(StatesGroup):
    PROFILE = State()
    GET_TASK_STAT = State()


class SendTaskSteps(StatesGroup):
    GET_TASK_NUMBER = State()
    GET_TASK_FILE = State()
