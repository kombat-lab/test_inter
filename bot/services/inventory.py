from __future__ import annotations

from dataclasses import replace
from math import ceil

from bot.models.inventory import InventoryItem, InventoryPage, ItemCategory

_CAPACITY = 100
_INITIAL_OCCUPIED_SLOTS = 77
_ITEMS_PER_PAGE = 5

_ITEMS = (
    InventoryItem(
        "poison_jar",
        "🧪",
        "Баночка с ядом",
        51,
        ItemCategory.RESOURCES,
        "Ядовитая жидкость, для безопасности закупоренная в пробирке. "
        "Вдохнув испарения, можно лично встретиться с каким-нибудь божеством.",
        "Обычный",
    ),
    InventoryItem(
        "white_fur",
        "⚪",
        "Белый мех",
        8,
        ItemCategory.RESOURCES,
        "Красивый белый мех. Роскошный материал для ремесла.",
        "Обычный",
    ),
    InventoryItem(
        "nest_resin",
        "🧪",
        "Гнездовая смола",
        1,
        ItemCategory.RESOURCES,
        "Странная густая жидкость. Такую можно найти возле гнезда.",
        "Обычный",
    ),
    InventoryItem(
        "rotting_meat",
        "🦠",
        "Гниющее мясо",
        14,
        ItemCategory.RESOURCES,
        "Мясо с невыносимым запахом. Не смей даже пробовать это. Без рецепта…",
        "Обычный",
    ),
    InventoryItem(
        "bitter_sap",
        "🫚",
        "Горькая сукровица",
        78,
        ItemCategory.RESOURCES,
        "Склянка с чьей-то сукровицей. Зачем ты её попробовал?",
        "Обычный",
    ),
    InventoryItem(
        "long_feather",
        "🪶",
        "Длинное перо",
        2,
        ItemCategory.RESOURCES,
        "Длинное и прочное перо. Материал для ремесла.",
        "Обычный",
    ),
    InventoryItem(
        "oak_leather",
        "🟫",
        "Дублёная кожа",
        1,
        ItemCategory.RESOURCES,
        "Толстое и плотное кожаное полотно. Кузнец наверняка знает, что с этим можно сделать.",
        "Обычный",
    ),
    InventoryItem(
        "burning_sap",
        "🧃",
        "Жгучий сок",
        42,
        ItemCategory.RESOURCES,
        "Сок, испарения которого обжигают глаза.",
        "Обычный",
    ),
    InventoryItem(
        "fog_staff",
        "🔵",
        "Жезл тумана",
        1,
        ItemCategory.EQUIPMENT,
        "Короткий посох, позволяющий концентрировать магическую энергию.",
        "🔵 Сверхредкий",
        ("Выносливость +4", "Магическая атака +2", "Магический урон +2.5%"),
        (
            "Интеллект: потеряете +2",
            "Выносливость: −1",
            "Удача: потеряете +1",
            "Магическая атака: +2",
            "Магический урон: +2.5%",
        ),
        equipment_slot="Основная рука",
    ),
    InventoryItem(
        "green_ichor",
        "🧪",
        "Зелёный ихор",
        16,
        ItemCategory.RESOURCES,
        "Ихор ярко-зелёного цвета.",
        "Обычный",
    ),
    InventoryItem(
        "snake_venom",
        "🐍",
        "Змеиный яд",
        15,
        ItemCategory.RESOURCES,
        "Змеиный яд, являющийся крайне опасным для всего живого.",
        "Обычный",
    ),
    InventoryItem(
        "golden_compass",
        "🧭",
        "Золотой компас",
        3,
        ItemCategory.CONSUMABLES,
        "Поговаривают, что стрелка компаса всегда приведёт вас к богатству.",
        "Необычный",
        ("Туманная пыль с монстров +25%", "Длительность 1ч"),
        usable=True,
    ),
    InventoryItem(
        "gold_chitin",
        "🛎",
        "Золотой хитин",
        39,
        ItemCategory.RESOURCES,
        "Необычный панцирь бронзовика. Похож на что-то драгоценное.",
        "Обычный",
    ),
    InventoryItem(
        "dried_chitin",
        "🥠",
        "Иссушенный хитин",
        99,
        ItemCategory.RESOURCES,
        "Интересно, что будет, если залить его водой? Материал для ремесла.",
        "Обычный",
    ),
    InventoryItem(
        "ancient_stone",
        "🟡",
        "Камень древнего знания",
        12,
        ItemCategory.RESOURCES,
        "Этот камень хранит отголоски прошлого и помогает раскрыть истинную суть вещей.",
        "Необычный",
    ),
    InventoryItem(
        "acid_proboscis",
        "🦠",
        "Кислотный хоботок",
        9,
        ItemCategory.RESOURCES,
        "Хоботок кислотной мухи. Он немного дымится, а зеленоватая тягучая "
        "жидкость стекает из него на землю.",
        "Необычный",
    ),
    InventoryItem(
        "leather_pants",
        "🔵",
        "Кожаные штаны",
        1,
        ItemCategory.EQUIPMENT,
        "Только в кожаных штанах…",
        "🔵 Сверхредкий",
        ("Интеллект +3", "Удача +4", "Защита +1", "Магическая защита +20"),
        (
            "Интеллект: +3",
            "Выносливость: потеряете +3",
            "Удача: +3",
            "Защита: −8",
            "Магическая защита: +15",
        ),
        equipment_slot="Штаны",
    ),
    InventoryItem(
        "berry_kissel",
        "🥣",
        "Кисель",
        9,
        ItemCategory.CONSUMABLES,
        "Варево из местных ягод. Выглядит безопасно, но никто не знает "
        "его точный состав. Восстанавливает немного здоровья.",
        "Обычный",
        ("Восстановление HP +75",),
        usable=True,
    ),
)

_quantity_overrides: dict[int, dict[str, int]] = {}
_equipped_items: dict[int, dict[str, str]] = {}


class InventoryOperationError(ValueError):
    """Raised when an inventory action cannot be completed."""


def _current_item(user_id: int, item: InventoryItem) -> InventoryItem:
    quantity = _quantity_overrides.get(user_id, {}).get(item.item_id, item.quantity)
    return replace(item, quantity=quantity)


def get_item(user_id: int, item_id: str) -> InventoryItem | None:
    return next((_current_item(user_id, item) for item in _ITEMS if item.item_id == item_id), None)


def get_inventory_page(
    user_id: int, *, category: ItemCategory = ItemCategory.ALL, query: str = "", page: int = 0
) -> InventoryPage:
    normalized_query = query.strip().casefold()
    current_items = [_current_item(user_id, item) for item in _ITEMS]
    items = [
        item
        for item in current_items
        if (category is ItemCategory.ALL or item.category is category)
        and (not normalized_query or normalized_query in item.name.casefold())
        and item.quantity > 0
    ]
    total_pages = max(1, ceil(len(items) / _ITEMS_PER_PAGE))
    page = min(max(page, 0), total_pages - 1)
    start = page * _ITEMS_PER_PAGE
    depleted = sum(item.quantity == 0 for item in current_items)
    return InventoryPage(
        tuple(items[start : start + _ITEMS_PER_PAGE]),
        page,
        total_pages,
        len(items),
        max(0, _INITIAL_OCCUPIED_SLOTS - depleted),
        _CAPACITY,
    )


def get_category_counts(user_id: int) -> dict[ItemCategory, int]:
    items = [item for item in (_current_item(user_id, item) for item in _ITEMS) if item.quantity]
    return {
        category: len(items)
        if category is ItemCategory.ALL
        else sum(item.category is category for item in items)
        for category in ItemCategory
    }


def use_item(user_id: int, item_id: str, quantity: int) -> InventoryItem:
    item = get_item(user_id, item_id)
    if item is None or not item.usable:
        raise InventoryOperationError("Этот предмет нельзя использовать.")
    if quantity <= 0 or quantity > item.quantity:
        raise InventoryOperationError("Недостаточно предметов.")
    new_quantity = item.quantity - quantity
    _quantity_overrides.setdefault(user_id, {})[item_id] = new_quantity
    return replace(item, quantity=new_quantity)


def toggle_equipped(user_id: int, item_id: str) -> bool:
    item = get_item(user_id, item_id)
    if item is None or item.equipment_slot is None:
        raise InventoryOperationError("Этот предмет нельзя экипировать.")
    equipment = _equipped_items.setdefault(user_id, {})
    if equipment.get(item.equipment_slot) == item_id:
        equipment.pop(item.equipment_slot)
        return False
    equipment[item.equipment_slot] = item_id
    return True


def is_equipped(user_id: int, item: InventoryItem) -> bool:
    return (
        item.equipment_slot is not None
        and _equipped_items.get(user_id, {}).get(item.equipment_slot) == item.item_id
    )


def reset_inventory_state() -> None:
    """Reset session-only mutations. Intended for deterministic tests."""
    _quantity_overrides.clear()
    _equipped_items.clear()
