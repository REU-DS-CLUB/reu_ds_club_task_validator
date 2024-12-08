from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import StartStep, ProfileStep
from bot.keyboards.keyboards import keyboard_start

from bot.utils.requests import get_tasks, get_user_assignments_by_task

router = Router()


@router.message(ProfileStep.PROFILE and F.text == "Список заданий")
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await get_tasks()
    await message.answer(text="Запрос на бэк по списку дел")


@router.message(ProfileStep.PROFILE and F.text == "Мои результаты")
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="Пришли номер задания")
    await state.set_state(ProfileStep.GET_TASK_STAT)


@router.message(ProfileStep.GET_TASK_STAT)
async def cases_ids(message: Message, state: FSMContext) -> None:
    if message.text and message.text.isdigit() and int(message.text.isdigit()) > 0:
        await message.answer(text=f"Номер задания {message.text}")
        # Запрос на бэк на сданные решения по задаче
        await get_user_assignments_by_task(int(message.text), str(message.from_user.id))
        await state.set_state(StartStep.MAIN)
    else:
        await message.answer(text="Неверные входные данные",
                             reply_markup=keyboard_start())
        await state.set_state(StartStep.MAIN)


@router.message(ProfileStep.PROFILE and F.text == "Назад")
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="Главная", reply_markup=keyboard_start())
    await state.set_state(StartStep.MAIN)