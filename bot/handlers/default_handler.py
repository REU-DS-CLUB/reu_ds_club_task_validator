from aiogram.types import Message
from aiogram import Router
from bot.keyboards.keyboards import keyboard_start
from bot.utils.states_forms import SendTaskSteps, StartStep, ProfileStep

router = Router()

@router.message()
async def get_start(message: Message) -> None:
    print(SendTaskSteps.GET_TASK_FILE)
    """Дефолтный ответ"""
    info = f"Ответ на все непонятные"
    await message.answer(text=info, reply_markup=keyboard_start())
