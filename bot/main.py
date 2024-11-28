import asyncio
from aiogram import Bot, Dispatcher

from bot.keyboards.keyboards import keyboard_start
from bot.handlers import handlers, default_handler, profile_handler, get_task_handler
dp = Dispatcher()
bot = Bot(token="")


async def start():
    dp.startup.register(keyboard_start)
    try:
        dp.include_routers(
            handlers.router,
            profile_handler.router,
            get_task_handler.router,
            default_handler.router
        )
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
