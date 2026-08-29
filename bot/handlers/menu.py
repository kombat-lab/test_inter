from __future__ import annotations

from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InaccessibleMessage, Message

from bot.callbacks.menu import MenuAction, MenuCallback
from bot.handlers.character import send_character_screen
from bot.keyboards.menu import back_to_menu_keyboard, main_menu_keyboard

router = Router(name=__name__)


async def _edit_screen(
    message: Message | InaccessibleMessage | None,
    text: str,
    *,
    main_menu: bool = False,
) -> None:
    if not isinstance(message, Message):
        return
    keyboard = main_menu_keyboard() if main_menu else back_to_menu_keyboard()
    await message.edit_text(text, reply_markup=keyboard)


@router.callback_query(MenuCallback.filter())
async def handle_menu(callback: CallbackQuery, callback_data: MenuCallback) -> None:
    await callback.answer()

    match callback_data.action:
        case MenuAction.HOME:
            await _edit_screen(
                callback.message,
                "<b>Главное меню</b>\n\nВыбери раздел:",
                main_menu=True,
            )
        case MenuAction.PLAY:
            await _edit_screen(
                callback.message,
                "<b>Новая игра</b>\n\nИгровая механика появится на следующем этапе.",
            )
        case MenuAction.CHARACTER:
            if isinstance(callback.message, Message):
                with suppress(TelegramBadRequest):
                    await callback.message.delete()
                await send_character_screen(callback.message)
        case MenuAction.HELP:
            await _edit_screen(
                callback.message,
                "<b>Помощь</b>\n\nИспользуй кнопки под сообщением для навигации.",
            )
