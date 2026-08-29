from __future__ import annotations

from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class MenuAction(StrEnum):
    HOME = "home"
    PLAY = "play"
    CHARACTER = "character"
    HELP = "help"


class MenuCallback(CallbackData, prefix="menu"):
    action: MenuAction
