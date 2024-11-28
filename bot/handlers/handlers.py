from aiogram.types import Message
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import SendTaskSteps, StartStep, ProfileStep
from bot.keyboards.keyboards import keyboard_profile, keyboard_start

import time

router = Router()

ids = {"id1": "data1", "id2": "data2"}

hi_ans = ""


@router.message(Command("start"))
async def get_start(message: Message, state: FSMContext) -> None:
    """Приветственное сообщение"""
    if message.from_user.username is not None:
        answer = f"Привет, {message.from_user.username}!\n"
    else:
        answer = "Привет!\n"

    answer += "Это бот для проверки твоих зданий по мл школе от REU DS Club"

    await message.answer(text=answer, reply_markup=keyboard_start())
    await state.set_state(StartStep.MAIN)


@router.message(StartStep.MAIN and F.text == "Мой профиль")
async def profile(message: Message, state: FSMContext) -> None:
    """Возврат в профиль пользователя"""
    await message.answer(text="хммм", reply_markup=keyboard_profile())
    await state.set_state(ProfileStep.PROFILE)


@router.message(StartStep.MAIN and F.text == "Сдать задание")
async def send_task(message: Message, state: FSMContext) -> None:
    """Начало сдачи задачи"""
    await message.answer("Пришли номер задания")
    await state.set_state(SendTaskSteps.GET_TASK_NUMBER)


@router.message(StartStep.MAIN)
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="хммм", reply_markup=keyboard_start())