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


def test_character_menu_matches_reference_layout() -> None:
    keyboard = character_keyboard()

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["📜 Квесты"],
        ["🎒 Инвентарь"],
        ["📊 Характеристики"],
        ["⚔️ Приемы"],
        ["🛡️ Экипировка"],
    ]
    assert [
        button.callback_data for row in keyboard.inline_keyboard for button in row
    ] == [
        "character:quests",
        "character:inventory",
        "character:stats",
        "character:skills",
        "character:equipment",
    ]
