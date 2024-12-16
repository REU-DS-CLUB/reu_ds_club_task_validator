from aiogram.types import Message
from aiogram import Router
from bot.keyboards.keyboards import keyboard_start

router = Router()


@router.message()
async def get_start(message: Message) -> None:
    """Дефолтный ответ"""
    info = f"Не понял"
    await message.answer(text=info, reply_markup=keyboard_start())
