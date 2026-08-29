from __future__ import annotations

import asyncio
from weakref import WeakValueDictionary

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message

_EDIT_LOCKS: WeakValueDictionary[tuple[int, int], asyncio.Lock] = WeakValueDictionary()
_BENIGN_EDIT_ERRORS = (
    "message is not modified",
    "canceled by new edit message request",
)


def _get_edit_lock(chat_id: int, message_id: int) -> asyncio.Lock:
    key = (chat_id, message_id)
    lock = _EDIT_LOCKS.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _EDIT_LOCKS[key] = lock
    return lock


def _is_benign_edit_error(error: TelegramBadRequest) -> bool:
    message = str(error).casefold()
    return any(marker in message for marker in _BENIGN_EDIT_ERRORS)


async def safe_edit_caption(
    message: Message,
    *,
    caption: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    async with _get_edit_lock(message.chat.id, message.message_id):
        try:
            await message.edit_caption(caption=caption, reply_markup=reply_markup)
        except TelegramBadRequest as error:
            if not _is_benign_edit_error(error):
                raise


async def safe_edit_media(
    message: Message,
    *,
    media: InputMediaPhoto,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    async with _get_edit_lock(message.chat.id, message.message_id):
        try:
            await message.edit_media(media=media, reply_markup=reply_markup)
        except TelegramBadRequest as error:
            if not _is_benign_edit_error(error):
                raise


async def safe_bot_edit_caption(
    bot: Bot,
    *,
    chat_id: int,
    message_id: int,
    caption: str,
    reply_markup: InlineKeyboardMarkup,
) -> None:
    async with _get_edit_lock(chat_id, message_id):
        try:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=caption,
                reply_markup=reply_markup,
            )
        except TelegramBadRequest as error:
            if not _is_benign_edit_error(error):
                raise
