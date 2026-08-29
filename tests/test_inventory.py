from __future__ import annotations

import pytest

from bot.keyboards.inventory import (
    inventory_filters_keyboard,
    inventory_item_keyboard,
    inventory_keyboard,
)
from bot.models.inventory import ItemCategory
from bot.services.characters import get_character
from bot.services.inventory import (
    InventoryOperationError,
    get_category_counts,
    get_inventory_page,
    get_item,
    is_equipped,
    reset_inventory_state,
    toggle_equipped,
    use_item,
)
from bot.views.inventory import (
    render_compare_caption,
    render_inventory_caption,
    render_item_caption,
)


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
    assert [button.text for button in keyboard.inline_keyboard[6]] == ["🔄 1 / 4", "▶️"]
    assert keyboard.inline_keyboard[0][0].text == "🔎 Поиск"


def test_inventory_filters_and_search() -> None:
    equipment = get_inventory_page(1, category=ItemCategory.EQUIPMENT)
    search = get_inventory_page(1, query="яд")

    assert {item.name for item in equipment.items} == {"Жезл тумана", "Кожаные штаны"}
    assert {item.name for item in search.items} == {"Баночка с ядом", "Змеиный яд"}


def test_empty_categories_are_hidden_from_filter() -> None:
    keyboard = inventory_filters_keyboard(get_category_counts(1), ItemCategory.ALL)
    labels = {button.text for row in keyboard.inline_keyboard for button in row}

    assert not any("Квестовые" in label for label in labels)
    assert not any("Карты" in label for label in labels)


def test_consumable_quantity_changes_in_session() -> None:
    item = use_item(7, "golden_compass", 1)

    assert item.quantity == 2
    assert get_item(7, "golden_compass").quantity == 2
    assert get_item(8, "golden_compass").quantity == 3


def test_equipment_can_be_equipped_and_removed() -> None:
    item = get_item(7, "fog_staff")
    assert item is not None

    assert toggle_equipped(7, item.item_id) is True
    assert is_equipped(7, item) is True
    assert toggle_equipped(7, item.item_id) is False
    assert is_equipped(7, item) is False


def test_item_card_uses_contextual_actions() -> None:
    consumable = get_item(1, "golden_compass")
    resource = get_item(1, "poison_jar")
    equipment = get_item(1, "fog_staff")
    assert consumable is not None
    assert resource is not None
    assert equipment is not None

    consumable_keyboard = inventory_item_keyboard(consumable)
    equipment_keyboard = inventory_item_keyboard(equipment)
    equipment_caption = render_item_caption(equipment)

    assert consumable_keyboard.inline_keyboard[0][0].text == "🧪 Использовать"
    assert inventory_item_keyboard(resource).inline_keyboard[0][0].text == "↩️ К предметам"
    assert [button.text for button in equipment_keyboard.inline_keyboard[0]] == [
        "🛡 Надеть",
        "⚖️ Сравнить",
    ]
    assert "Выносливость +4" in equipment_caption
    assert "Слот: <b>Основная рука</b>" in equipment_caption
    assert "Жезл тумана · +6" in equipment_caption
    assert "Требуемый уровень: <b>1</b>" in equipment_caption
    assert "Аколит, Ученик Аколита" in equipment_caption
    assert "Личный предмет · нельзя передать" in equipment_caption
    comparison = render_compare_caption(equipment, equipped=False)
    assert "Сейчас надето:</b> Витой тотем" in comparison
    assert "Магическая атака: +2" in comparison


def test_leather_pants_card_uses_production_details() -> None:
    item = get_item(1, "leather_pants")
    assert item is not None

    caption = render_item_caption(item)
    comparison = render_compare_caption(item, equipped=False)

    assert "Требуемый уровень: <b>10</b>" in caption
    assert "Аколит, Бастион, Охотник, Маг, Тень" in caption
    assert "Магическая защита +20" in caption
    assert "Сейчас надето:</b> Плотные штаны" in comparison
    assert "Защита: −8" in comparison


def test_crafting_resource_cannot_be_used() -> None:
    with pytest.raises(InventoryOperationError):
        use_item(1, "poison_jar", 1)


def test_removed_map_is_not_in_inventory() -> None:
    all_items = [item for page in range(4) for item in get_inventory_page(1, page=page).items]

    assert "Карта затонувшего храма" not in {item.name for item in all_items}
    assert "Кисель" in {item.name for item in all_items}
