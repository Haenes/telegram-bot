import os
import asyncio
import logging
import requests

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_BASE_URL = "http://127.0.0.1:8000/api"


logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def get_token(username, password):
    data = {
        "username": username,
        "password": password
	}
    r = requests.post(f"{API_BASE_URL}-token-auth/", json=data)
    token = r.json()["token"]

    # return token
    os.environ["API_TOKEN"] = token


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("In development")


@dp.message(Command("login"))
async def cmd_login(message: types.Message, command:CommandObject):
    if command.args:
        data = command.args.split(" ")
        username, password = data[0], data[1]

        try:
            get_token(username, password)
            await message.reply("Successful login! \nTo continue, enter /menu command.")
        except KeyError:
            await message.reply("Invalid username/password!")

    else:
        await message.answer("Please, enter your username and password after /login command!\nExample: /login *YOUR USERNAME* *YOUR PASSWORD*")



@dp.message(Command("menu"))
async def cmd_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Projects",
        callback_data="projects"
        )
    )

    builder.add(types.InlineKeyboardButton(
        text="Issues",
        callback_data="issues"
        )
    )
    await message.answer("From here, u can see all of yours Projects and Issues", reply_markup=builder.as_markup())


def get_projects(headers, **kwargs):
    r = requests.get(f"{API_BASE_URL}/projects", headers=headers, **kwargs)
    return r.json()


@dp.callback_query(F.data == "projects")
async def send_projects(callback: types.CallbackQuery):
    token = os.environ.get('API_TOKEN')
    HEADERS = {"Authorization": f"Token {token}"}

    results = get_projects(headers=HEADERS)
    print(results)
    projects = [project for project in results["results"]]

    builder = InlineKeyboardBuilder()

    for p in projects:
        builder.add(types.InlineKeyboardButton(
            text=p["name"],
            callback_data="project"
            )
        )
    builder.adjust(2)

    if results["next"] != None:
        builder.row(types.InlineKeyboardButton(
            text="Next >>",
            callback_data="next"
            )
        )
    
    if results["previous"] != None:
        builder.add(types.InlineKeyboardButton(
            text="<< Back",
            callback_data="back"
            )
        )

    await callback.message.answer("List of projects:", reply_markup=builder.as_markup())
    # await callback.message.answer("P!")

    await callback.answer()


@dp.callback_query(F.data == "issues")
async def send_issues(callback: types.CallbackQuery):
    await callback.message.answer("I!")
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
