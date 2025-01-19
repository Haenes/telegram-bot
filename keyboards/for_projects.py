from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _


def project_favorite_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    texts = ["True", "False"]

    for text in texts:
        builder.add(
            InlineKeyboardButton(
                text=_(text),
                callback_data=f"prj_favorite_{text}"
            )
        )

    return builder.as_markup()
