from __future__ import annotations

from aiogram import Dispatcher

from bot.handlers.menu import router as menu_router
from bot.handlers.start import router as start_router


def register_routers(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(start_router, menu_router)
