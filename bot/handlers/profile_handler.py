from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from bot.utils.states_forms import StartStep, ProfileStep
from bot.keyboards.keyboards import keyboard_start, keyboard_profile

from bot.utils.requests import get_tasks, get_task, get_results, get_assignments

router = Router()


@router.message(ProfileStep.PROFILE and F.text == "Список заданий")
async def cases_ids(message: Message) -> None:
    """Вывод название кейсов и их айдишки"""
    tasks = await get_tasks()
    await message.answer(text=str(tasks))


@router.message(ProfileStep.PROFILE and F.text == "Информация по заданию")
async def case_info(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="Пришли номер задания")
    await state.set_state(ProfileStep.GET_TASK_INFO)


@router.message(ProfileStep.GET_TASK_INFO)
async def send_case_info(message: Message, state: FSMContext) -> None:
    if message.text and message.text.isdigit() and int(message.text.isdigit()) > 0:
        response = await get_task(task_id=int(message.text))
        if response.status_code == 200:
            data = response.json()
            await message.answer(text=str(data))
        else:
            await message.answer(f"Произошла ошибка: {response.text}")
        await state.set_state(ProfileStep.PROFILE)
    else:
        await message.answer(text="Неверные входные данные",
                             reply_markup=keyboard_profile())
        await state.set_state(ProfileStep.PROFILE)


@router.message(ProfileStep.PROFILE and F.text == "Мои решения по заданию")
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="Пришли номер задания")
    await state.set_state(ProfileStep.GET_TASK_STAT)


@router.message(ProfileStep.GET_TASK_STAT)
async def cases_ids(message: Message, state: FSMContext) -> None:
    if message.text and message.text.isdigit() and int(message.text.isdigit()) > 0:
        response = await get_assignments(task_id=int(message.text), tg_id=str(message.from_user.id))
        if response.status_code == 200:
            data = response.json()
            await message.answer(text=str(data))
        else:
            await message.answer(f"Произошла ошибка: {response.text}")
        await state.set_state(ProfileStep.PROFILE)
    else:
        await message.answer(text="Неверные входные данные",
                             reply_markup=keyboard_profile())
        await state.set_state(ProfileStep.PROFILE)


@router.message(ProfileStep.PROFILE and F.text == "Назад")
async def cases_ids(message: Message, state: FSMContext) -> None:
    """Вывод название кейсов и их айдишки"""
    await message.answer(text="Главная", reply_markup=keyboard_start())
    await state.set_state(StartStep.MAIN)


@router.message(ProfileStep.PROFILE and F.text == "Мои результаты")
async def cases_ids(message: Message) -> None:
    """Вывод название кейсов и их айдишки"""
    response = await get_results(tg_id=str(message.from_user.id))
    if response.status_code == 200:
        data = response.json()
        await message.answer(text=str(data))
    else:
        await message.answer(f"Произошла ошибка: {response.text}")
