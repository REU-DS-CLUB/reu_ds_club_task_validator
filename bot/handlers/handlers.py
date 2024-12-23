from datetime import datetime, date

from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import SendTaskSteps, StartStep, ProfileStep
from bot.keyboards.keyboards import keyboard_profile, keyboard_start

from bot.utils.get_username import get_username
from bot.utils.requests import is_newbie, add_user

from bot.text_bot import FULL_INFORMATION, INSTRUCTION

router = Router()

COOLDOWN = 1


@router.message(Command("start"))
async def get_start(message: Message, state: FSMContext) -> None:
    """Приветственное сообщение"""
    ans_is_newbie = await is_newbie(str(message.from_user.id))
    if ans_is_newbie:
        ans_add_user = await add_user(str(message.from_user.id), str(message.from_user.username))
        await message.answer(f"ans_add_user: {str(ans_add_user)}")

    username = await get_username(message)
    if username is not None:
        answer = f"Привет, {username}!\n\n"
    else:
        answer = "Привет!\n\n"
    answer += INSTRUCTION

    await message.answer(text=answer, reply_markup=keyboard_start())
    await state.set_state(StartStep.MAIN)
    await state.update_data(last_assignment=datetime(year=2024, month=12, day=11))


@router.message(StartStep.MAIN and F.text == "Мой профиль")
async def profile(message: Message, state: FSMContext) -> None:
    """Возврат в профиль пользователя"""
    answer = "Профиль "

    username = await get_username(message)
    if username is not None:
        answer += username
    else:
        answer += "пользователя"

    await message.answer(text=answer, reply_markup=keyboard_profile())
    await state.set_state(ProfileStep.PROFILE)


async def check_last_last_assignment(state: FSMContext) -> int:
    data = await state.get_data()
    last_asg = data["last_assignment"]
    seconds = (datetime.now() - last_asg).total_seconds()
    if seconds > 60 * COOLDOWN:
        return 0
    return int(60 * COOLDOWN - seconds)


@router.message(StartStep.MAIN and F.text == "Сдать задание")
async def send_task(message: Message, state: FSMContext) -> None:
    """Начало сдачи задачи"""
    wait = await check_last_last_assignment(state)
    if wait == 0:
        await state.update_data(last_assignment=datetime.now())
        await message.answer("Пришли номер задания")
        await state.set_state(SendTaskSteps.GET_TASK_NUMBER)
    else:
        await message.answer(f"Перед новой отправкой задания должно пройти еще {wait} секунд")


@router.message(StartStep.MAIN and F.text == "Информация")
async def get_information(message: Message) -> None:
    """Информация по боту"""
    await message.answer(FULL_INFORMATION)
