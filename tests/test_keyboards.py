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
    keyboard = character_keyboard(effects_count=3, has_claimable_quest=True)

    assert [[button.text for button in row] for row in keyboard.inline_keyboard] == [
        ["⚡ Все эффекты · 3"],
        ["🎒 Инвентарь", "🛡 Экипировка"],
        ["📊 Параметры", "⚔️ Приёмы"],
        ["📜 Квесты"],
    ]
    assert [button.callback_data for row in keyboard.inline_keyboard for button in row] == [
        "character:effects",
        "character:inventory",
        "character:equipment",
        "character:stats",
        "character:skills",
        "character:quests",
    ]
    assert keyboard.inline_keyboard[1][1].style is None
    assert keyboard.inline_keyboard[-1][0].style == "success"


def test_quests_button_is_neutral_without_claimable_quest() -> None:
    keyboard = character_keyboard(effects_count=3, has_claimable_quest=False)

    assert keyboard.inline_keyboard[-1][0].text == "📜 Квесты"
    assert keyboard.inline_keyboard[-1][0].style is None


def test_expanded_effects_keyboard_can_return_to_overview() -> None:
    keyboard = character_keyboard(effects_count=3, effects_expanded=True)

    assert keyboard.inline_keyboard[0][0].text == "⚡ Свернуть эффекты"
    assert keyboard.inline_keyboard[0][0].callback_data == "character:overview"
