import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers import start, projects, issues


async def main():
    load_dotenv()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(start.router, projects.router, issues.router)

    # Launch the bot and skip all the accumulated updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
