from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks.character import CharacterCallback, CharacterSection


def _button(
    text: str,
    section: CharacterSection,
    *,
    style: str | None = None,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=CharacterCallback(section=section).pack(),
        style=style,
    )


def stats_keyboard(*, expanded: bool = False) -> InlineKeyboardMarkup:
    details_text = "📊 Свернуть" if expanded else "📋 Все показатели"
    details_section = CharacterSection.STATS if expanded else CharacterSection.STATS_DETAILS
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_button(details_text, details_section)],
            [
                _button("🛡 Экипировка", CharacterSection.EQUIPMENT),
                _button("⚔️ Приёмы", CharacterSection.SKILLS),
            ],
            [_button("↩️ Персонаж", CharacterSection.OVERVIEW, style="primary")],
        ]
    )
