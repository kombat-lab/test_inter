from __future__ import annotations

from bot.keyboards.menu import main_menu_keyboard


def test_main_menu_contains_expected_actions() -> None:
    keyboard = main_menu_keyboard()
    callback_values = {
        button.callback_data
        for row in keyboard.inline_keyboard
        for button in row
        if button.callback_data is not None
    }

    assert callback_values == {"menu:play", "menu:profile", "menu:help"}
