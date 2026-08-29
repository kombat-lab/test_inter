from __future__ import annotations

import pytest

from bot.keyboards.inventory import inventory_item_keyboard, inventory_keyboard
from bot.models.inventory import ItemCategory
from bot.services.characters import get_character
from bot.services.inventory import (
    get_inventory_page,
    get_item,
    is_equipped,
    reset_inventory_state,
    toggle_equipped,
    use_item,
)
from bot.views.inventory import render_inventory_caption, render_item_caption


@pytest.fixture(autouse=True)
def reset_inventory() -> None:
    reset_inventory_state()


def test_inventory_page_is_compact_and_paginated() -> None:
    inventory = get_inventory_page(1)
    caption = render_inventory_caption(inventory, get_character(), ItemCategory.ALL)
    keyboard = inventory_keyboard(inventory, ItemCategory.ALL)

    assert inventory.page == 0
    assert inventory.total_pages == 4
    assert len(inventory.items) == 5
    assert "Инвентарь · 77/100" in caption
    assert "Все предметы</b> · 18" in caption
    assert "Баночка с ядом" not in caption
    assert len(keyboard.inline_keyboard) == 9
    assert keyboard.inline_keyboard[1][0].text == "🧪 Баночка с ядом · 51"
    assert [button.text for button in keyboard.inline_keyboard[6]] == ["1 / 4", "▶️"]


def test_inventory_filters_and_search() -> None:
    equipment = get_inventory_page(1, category=ItemCategory.EQUIPMENT)
    search = get_inventory_page(1, query="яд")

    assert {item.name for item in equipment.items} == {"Жезл тумана", "Кожаные штаны"}
    assert {item.name for item in search.items} == {"Баночка с ядом", "Змеиный яд"}


def test_consumable_quantity_changes_in_session() -> None:
    item = use_item(7, "poison_jar", 5)

    assert item.quantity == 46
    assert get_item(7, "poison_jar").quantity == 46
    assert get_item(8, "poison_jar").quantity == 51


def test_equipment_can_be_equipped_and_removed() -> None:
    item = get_item(7, "fog_staff")
    assert item is not None

    assert toggle_equipped(7, item.item_id) is True
    assert is_equipped(7, item) is True
    assert toggle_equipped(7, item.item_id) is False
    assert is_equipped(7, item) is False


def test_item_card_uses_contextual_actions() -> None:
    consumable = get_item(1, "poison_jar")
    equipment = get_item(1, "fog_staff")
    assert consumable is not None
    assert equipment is not None

    consumable_keyboard = inventory_item_keyboard(consumable)
    equipment_keyboard = inventory_item_keyboard(equipment)
    equipment_caption = render_item_caption(equipment)

    assert consumable_keyboard.inline_keyboard[0][0].text == "🧪 Использовать"
    assert [button.text for button in equipment_keyboard.inline_keyboard[0]] == [
        "🛡 Надеть",
        "⚖️ Сравнить",
    ]
    assert "Сила +4" in equipment_caption
    assert "Слот: <b>Оружие</b>" in equipment_caption
