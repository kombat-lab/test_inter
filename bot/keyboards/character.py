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


def character_keyboard(
    *,
    effects_count: int = 0,
    effects_expanded: bool = False,
    has_claimable_quest: bool = False,
) -> InlineKeyboardMarkup:
    effects_text = (
        "⚡ Свернуть эффекты" if effects_expanded else f"⚡ Все эффекты · {effects_count}"
    )
    effects_section = CharacterSection.OVERVIEW if effects_expanded else CharacterSection.EFFECTS
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_button(effects_text, effects_section)],
            [
                _button("🎒 Инвентарь", CharacterSection.INVENTORY),
                _button("🛡 Экипировка", CharacterSection.EQUIPMENT),
            ],
            [
                _button("📊 Параметры", CharacterSection.STATS),
                _button("⚔️ Приёмы", CharacterSection.SKILLS),
            ],
            [
                _button(
                    "📜 Квесты",
                    CharacterSection.QUESTS,
                    style="success" if has_claimable_quest else None,
                )
            ],
        ]
    )


def character_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_button("← Персонаж", CharacterSection.OVERVIEW, style="primary")],
        ]
    )
