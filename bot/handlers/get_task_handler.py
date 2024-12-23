from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import StartStep, SendTaskSteps
from bot.keyboards.keyboards import keyboard_start
from bot.utils.requests import submit_assignment
import os

router = Router()


@router.message(SendTaskSteps.GET_TASK_NUMBER)
async def get_task_number(message: Message, state: FSMContext) -> None:
    if message.text.isdigit() and int(message.text) > 0:
        await message.answer("Пришли файлик со своим решением")
        await state.update_data(task_id=int(message.text))
        await state.set_state(SendTaskSteps.GET_TASK_FILE)
    else:
        await message.answer(text="Неверные входные данные", reply_markup=keyboard_start())
        await state.set_state(StartStep.MAIN)


@router.message(SendTaskSteps.GET_TASK_FILE)
async def get_task_file(message: Message, bot: Bot, state: FSMContext) -> None:
    if message.document \
        and len(message.document.file_name.split(".")) == 2 \
            and message.document.file_name.endswith((".py", ".csv")):

        mess_id = message.message_id # Get messsage id type int

        answer = "💨Обрабатываю ваш запрос..."
        temp_message = await message.reply(answer)

        data = await state.get_data()
        task_id = data["task_id"]
        tg_id = str(message.from_user.id)

        doc_type = message.document.file_name.split('.')[-1]
        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        file_holder = f"{os.path.dirname(os.path.abspath(__file__))}\\user_docs\\"
        path = f"{file_holder}{str(file_id)}.{doc_type}"
        await bot.download_file(file.file_path, path)

        answer = await submit_assignment(task_id=task_id, tg_id=tg_id, assignment_file=path)
        os.remove(path)

        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=temp_message.message_id)
        await message.reply(text=f"Результат обработки!: {answer}", reply_to_message_id=mess_id)
        await state.set_state(StartStep.MAIN)
    else:
        await message.answer(text="Это не документ", reply_markup=keyboard_start())
        await state.set_state(StartStep.MAIN)
