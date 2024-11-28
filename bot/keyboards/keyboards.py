from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def keyboard_start():
    kb = [
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Сдать задание")],
        [KeyboardButton(text="Информация")]
        # [KeyboardButton(text="Получить описание задания")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb,
                               resize_keyboard=True,
                               input_field_placeholder="Воспользуйтесь меню:")


def keyboard_profile():
    kb = [
        [KeyboardButton(text="Список заданий")],
        [KeyboardButton(text="Мои результаты")],
        [KeyboardButton(text="Назад")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# def keyboard_cancel():
#     kb = [
#         [KeyboardButton(text="Назад")]
#     ]
#     return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
