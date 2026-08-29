from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.menu import MenuAction, MenuCallback


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎮 Начать игру",
        callback_data=MenuCallback(action=MenuAction.PLAY),
    )
    builder.button(
        text="👤 Профиль",
        callback_data=MenuCallback(action=MenuAction.PROFILE),
    )
    builder.button(
        text="❓ Помощь",
        callback_data=MenuCallback(action=MenuAction.HELP),
    )
    builder.adjust(1, 2)
    return builder.as_markup()


def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="← В главное меню",
        callback_data=MenuCallback(action=MenuAction.HOME),
    )
    return builder.as_markup()
