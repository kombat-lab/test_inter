from __future__ import annotations

from bot.keyboards.character import character_keyboard
from bot.keyboards.menu import main_menu_keyboard


def test_main_menu_contains_expected_actions() -> None:
    keyboard = main_menu_keyboard()
    callback_values = {
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
        if button.callback_data is not None
    }

    assert callback_values == {"menu:play", "menu:character", "menu:help"}


def test_character_menu_uses_compact_styled_layout() -> None:
    keyboard = character_keyboard()

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["🎒 Инвентарь", "🛡 Экипировка"],
        ["📊 Характеристики", "⚔️ Приёмы"],
        ["⚡ Все эффекты · 3"],
        ["📜 Перейти к квестам"],
    ]
    assert [
        button.callback_data for row in keyboard.inline_keyboard for button in row
    ] == [
        "character:inventory",
        "character:equipment",
        "character:stats",
        "character:skills",
        "character:effects",
        "character:quests",
    ]
    assert keyboard.inline_keyboard[0][1].style == "success"
    assert keyboard.inline_keyboard[-1][0].style == "primary"


def test_expanded_effects_keyboard_can_return_to_overview() -> None:
    keyboard = character_keyboard(effects_expanded=True)

    assert keyboard.inline_keyboard[2][0].text == "⚡ Свернуть эффекты"
    assert keyboard.inline_keyboard[2][0].callback_data == "character:overview"
