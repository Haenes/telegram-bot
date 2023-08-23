from aiogram import Router, types
from aiogram.filters import CommandObject
from aiogram.filters.command import Command

from handlers.bugtracker_api import get_token
from keyboards.for_menu import menu_kb


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("In development")


@router.message(Command("login"))
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
        await message.answer("Please, enter your username and password after /login command! \nExample: /login *YOUR USERNAME* *YOUR PASSWORD*")


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
	await message.answer("From here, u can see all of yours Projects and Issues", reply_markup=menu_kb())
