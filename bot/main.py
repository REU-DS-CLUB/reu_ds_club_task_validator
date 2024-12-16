import asyncio
from aiogram import Bot, Dispatcher
import os

from bot.keyboards.keyboards import keyboard_start
from bot.handlers import handlers, default_handler, profile_handler, get_task_handler

from bot.text_bot import BOT_DESCRIPTION
dp = Dispatcher()

bot = Bot(token=os.getenv("BOT_TOKEN"))


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
        await bot.set_my_description(BOT_DESCRIPTION)
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())
