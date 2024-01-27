from aiogram import Router, types
from aiogram.filters import CommandObject
from aiogram.filters.command import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from handlers.bugtracker_api import get_token
from keyboards.for_menu import menu_kb


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user = message.from_user.first_name

    text = _("""
\nA quick guide to working with me: 
\n1) Login: first step is log in via /login command. \n    Without it, I won't work!
\n2) Main menu accessed via /menu command. \n    Here you can choose what to work with: projects or issues.
\n3) After your choice, you will be able to create a new element \n    (project or issue, depending on what you have chosen) \n    and view information about it.
\n4) After the next selection, you can change the data of the element \n    or delete it altogether!
\n<b>Please note that you must already be registered through the website. If you don't have an account yet, then you need to create one and only then use me </b>
           """)

    # await message.answer(f"Hello, {user}! {text}", parse_mode="HTML")
    await message.answer(_("Hello, {user}! {text}").format(user=user, text=text), parse_mode="HTML")


@router.message(Command("login"))
async def cmd_login(message: types.Message, command:CommandObject):
    if command.args:
        data = command.args.split(" ")
        username, password = data[0], data[1]

        try:
            get_token(username, password)
            await message.reply(_("Successful login! \nTo continue, enter /menu command."))
        except KeyError:
            await message.reply(_("Invalid username/password!"))

    else:
        await message.answer(_("Please, enter your <u>username and password</u> after /login command! \nExample: /login USERNAME PASSWORD"), parse_mode="HTML")


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
	await message.answer(_("From here, u can see all of yours <b>Projects</b> and <b>Issues</b>."), parse_mode="HTML", reply_markup=menu_kb())
