from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import StartStep, ProfileStep, SendTaskSteps
from bot.keyboards.keyboards import keyboard_start
import time

router = Router()


@router.message(SendTaskSteps.GET_TASK_NUMBER)
async def get_task_number(message: Message, state: FSMContext) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        await message.answer("Пришли файлик со своим решением")
        await state.set_state(SendTaskSteps.GET_TASK_FILE)
    else:
        await message.answer(text="Неверные входные данные", reply_markup=keyboard_start())
        await state.set_state(StartStep.MAIN)


@router.message(SendTaskSteps.GET_TASK_FILE)
async def get_task_file(message: Message, bot: Bot, state: FSMContext) -> None:
    if message.document:
        answer = "💨Обрабатываю ваш запрос..."
        temp_message = await message.reply(answer)
        time.sleep(5)
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=temp_message.message_id)
        await message.answer("Результат обработки!")
        await state.set_state(StartStep.MAIN)
    else:
        await message.answer(text="Это не документ", reply_markup=keyboard_start())
        await state.set_state(StartStep.MAIN)
