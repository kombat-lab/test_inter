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
        ItemCategory.CONSUMABLES,
        "Покрывает оружие ядом и усиливает следующий удар.",
        "Необычный",
        ("Яд на 3 хода",),
        usable=True,
    ),
    InventoryItem(
        "white_fur",
        "⚪",
        "Белый мех",
        8,
        ItemCategory.RESOURCES,
        "Редкий мех для ремесла и обмена у торговцев.",
        "Обычный",
    ),
    InventoryItem(
        "nest_resin",
        "🧪",
        "Гнездовая смола",
        1,
        ItemCategory.CONSUMABLES,
        "Липкая алхимическая основа из туманных гнёзд.",
        "Необычный",
        ("Компонент алхимии",),
        usable=True,
    ),
    InventoryItem(
        "rotting_meat",
        "🦠",
        "Гниющее мясо",
        14,
        ItemCategory.CONSUMABLES,
        "Резко пахнущая приманка для существ тумана.",
        "Обычный",
        ("Приманка",),
        usable=True,
    ),
    InventoryItem(
        "bitter_sap",
        "🍂",
        "Горькая сукровица",
        78,
        ItemCategory.CONSUMABLES,
        "Горький экстракт, восстанавливающий силы в пути.",
        "Обычный",
        ("Восстановление энергии",),
        usable=True,
    ),
    InventoryItem(
        "long_feather",
        "🪶",
        "Длинное перо",
        2,
        ItemCategory.RESOURCES,
        "Прочное перо крупной болотной птицы.",
        "Обычный",
    ),
    InventoryItem(
        "oak_leather",
        "🟫",
        "Дублёная кожа",
        1,
        ItemCategory.RESOURCES,
        "Выделанная кожа для починки лёгкой брони.",
        "Обычный",
    ),
    InventoryItem(
        "burning_sap",
        "🧃",
        "Жгучий сок",
        42,
        ItemCategory.QUEST,
        "Образец сока, собранный для поручения травницы.",
        "Квестовый",
    ),
    InventoryItem(
        "fog_staff",
        "🔵",
        "Жезл тумана",
        1,
        ItemCategory.EQUIPMENT,
        "Фокусирует туман и усиливает способности аколита.",
        "Редкий",
        ("Сила +4", "Магия +2", "Эффект тумана +2.5%"),
        equipment_slot="Оружие",
    ),
    InventoryItem(
        "green_ichor",
        "🧪",
        "Зелёный ихор",
        16,
        ItemCategory.CONSUMABLES,
        "Нестабильная жидкость для боевых смесей.",
        "Необычный",
        ("Урон способности +10%",),
        usable=True,
    ),
    InventoryItem(
        "snake_venom",
        "🐍",
        "Змеиный яд",
        15,
        ItemCategory.CONSUMABLES,
        "Концентрированный яд туманной змеи.",
        "Необычный",
        ("Яд на 5 ходов",),
        usable=True,
    ),
    InventoryItem(
        "golden_compass",
        "🧭",
        "Золотой компас",
        3,
        ItemCategory.QUEST,
        "Указывает путь к отмеченной области задания.",
        "Квестовый",
    ),
    InventoryItem(
        "gold_chitin",
        "🟡",
        "Золотой хитин",
        39,
        ItemCategory.RESOURCES,
        "Твёрдая пластина для усиления брони.",
        "Редкий",
    ),
    InventoryItem(
        "dried_chitin",
        "🟤",
        "Иссушенный хитин",
        99,
        ItemCategory.RESOURCES,
        "Лёгкий ремесленный материал.",
        "Обычный",
    ),
    InventoryItem(
        "ancient_stone",
        "🟡",
        "Камень древнего знания",
        12,
        ItemCategory.QUEST,
        "Хранит фрагмент памяти исчезнувшего ордена.",
        "Квестовый",
    ),
    InventoryItem(
        "acid_proboscis",
        "🦠",
        "Кислотный хоботок",
        9,
        ItemCategory.RESOURCES,
        "Орган туманного насекомого с остатками кислоты.",
        "Необычный",
    ),
    InventoryItem(
        "leather_pants",
        "🔵",
        "Кожаные штаны",
        1,
        ItemCategory.EQUIPMENT,
        "Лёгкая защита, не мешающая движению.",
        "Необычный",
        ("Защита +3", "Ловкость +4", "Сопротивление +1"),
        equipment_slot="Ноги",
    ),
    InventoryItem(
        "sunken_temple_map",
        "🗺",
        "Карта затонувшего храма",
        1,
        ItemCategory.CARDS,
        "Открывает маршрут к затонувшему храму.",
        "Редкий",
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
