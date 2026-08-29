from __future__ import annotations

from html import escape

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.keyboards.menu import main_menu_keyboard

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    user_name = escape(message.from_user.full_name) if message.from_user else "игрок"
    await message.answer(
        f"Привет, <b>{user_name}</b>!\n\n"
        "Это основа игрового Telegram-бота. Выбери раздел:",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    await message.answer(
        "<b>Доступные команды</b>\n\n"
        "/start — открыть главное меню\n"
        "/character — открыть персонажа\n"
        "/help — показать эту справку",
        reply_markup=main_menu_keyboard(),
    )
