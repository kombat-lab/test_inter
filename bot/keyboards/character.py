from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks.character import CharacterCallback, CharacterSection


def character_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    buttons = (
        ("📜 Квесты", CharacterSection.QUESTS),
        ("🎒 Инвентарь", CharacterSection.INVENTORY),
        ("📊 Характеристики", CharacterSection.STATS),
        ("⚔️ Приемы", CharacterSection.SKILLS),
        ("🛡️ Экипировка", CharacterSection.EQUIPMENT),
    )
    for text, section in buttons:
        builder.button(
            text=text,
            callback_data=CharacterCallback(section=section),
        )
    builder.adjust(1)
    return builder.as_markup()
