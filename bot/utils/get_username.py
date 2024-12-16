from aiogram.types import Message


async def get_username(message: Message) -> None | str:
    """Возврат в профиль пользователя"""
    username = None
    if message.from_user.first_name is not None:
        username = str(message.from_user.first_name)
        if message.from_user.last_name is not None:
            username += f" {message.from_user.last_name}"
    elif message.from_user.username is not None:
        username = str(message.from_user.username)
    return username
