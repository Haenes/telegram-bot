import os
import asyncio
import logging

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from handlers import start, projects, pagination_projects, issues, pagination_issues, common, create_project, update_project, create_issue, update_issue


async def main():
    load_dotenv()
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_routers(start.router, projects.router, pagination_projects.router, issues.router, pagination_issues.router)
    dp.include_routers(common.router, create_project.router, update_project.router, create_issue.router, update_issue.router)


    # Launch the bot and skip all the accumulated updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
