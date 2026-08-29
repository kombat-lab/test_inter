from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks.character import CharacterCallback, CharacterSection
from bot.callbacks.inventory import InventoryAction, InventoryCallback
from bot.models.inventory import InventoryItem, InventoryPage, ItemCategory


def _callback_button(
    text: str, action: InventoryAction, value: str = "", *, style: str | None = None
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text, callback_data=InventoryCallback(action=action, value=value).pack(), style=style
    )


def _item_text(item: InventoryItem) -> str:
    name = item.name if len(item.name) <= 27 else f"{item.name[:26]}…"
    return f"{item.icon} {name} · {item.quantity}"


def inventory_keyboard(
    inventory: InventoryPage, category: ItemCategory, *, query: str = ""
) -> InlineKeyboardMarkup:
    search_action = InventoryAction.CLEAR_SEARCH if query else InventoryAction.SEARCH
    search_text = "✕ Сбросить" if query else "🔎 Поиск"
    rows = [[_callback_button(search_text, search_action)]]
    rows.extend(
        [_callback_button(_item_text(item), InventoryAction.ITEM, item.item_id)]
        for item in inventory.items
    )
    if inventory.total_pages > 1:
        navigation = []
        if inventory.page > 0:
            navigation.append(
                _callback_button("◀️", InventoryAction.PAGE, str(inventory.page - 1)),
            )
        navigation.append(
            _callback_button(
                f"🔄 {inventory.page + 1} / {inventory.total_pages}",
                InventoryAction.REFRESH,
            )
        )
        if inventory.page < inventory.total_pages - 1:
            navigation.append(
                _callback_button("▶️", InventoryAction.PAGE, str(inventory.page + 1)),
            )
        rows.append(navigation)
    rows.extend(
        [
            [
                _callback_button(
                    f"{category.icon} Категория: {category.title}", InventoryAction.FILTERS
                )
            ],
            [
                InlineKeyboardButton(
                    text="↩️ Персонаж",
                    callback_data=CharacterCallback(section=CharacterSection.OVERVIEW).pack(),
                    style="primary",
                )
            ],
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def inventory_filters_keyboard(
    counts: dict[ItemCategory, int], current: ItemCategory
) -> InlineKeyboardMarkup:
    rows = [
        [
            _callback_button(
                f"{category.icon} {category.title} · {counts[category]}",
                InventoryAction.CATEGORY,
                category.value,
                style="success" if category is current else None,
            )
        ]
        for category in ItemCategory
        if counts[category] > 0 or category is current
    ]
    rows.append([_callback_button("↩️ К предметам", InventoryAction.BACK_LIST)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def inventory_item_keyboard(item: InventoryItem, *, equipped: bool = False) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if item.usable and item.quantity:
        rows.append(
            [
                _callback_button(
                    "🧪 Использовать", InventoryAction.USE_MENU, item.item_id, style="success"
                )
            ]
        )
    if item.equipment_slot:
        rows.append(
            [
                _callback_button(
                    "📥 Снять" if equipped else "🛡 Надеть",
                    InventoryAction.EQUIP,
                    item.item_id,
                    style=None if equipped else "success",
                ),
                _callback_button("⚖️ Сравнить", InventoryAction.COMPARE, item.item_id),
            ]
        )
    rows.append([_callback_button("↩️ К предметам", InventoryAction.BACK_LIST)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def inventory_quantity_keyboard(item: InventoryItem) -> InlineKeyboardMarkup:
    amounts = tuple(amount for amount in (1, 5, 10) if amount <= item.quantity)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _callback_button(
                    f"×{amount}", InventoryAction.USE, f"{item.item_id}.{amount}", style="success"
                )
                for amount in amounts
            ],
            [_callback_button("↩️ К предмету", InventoryAction.ITEM, item.item_id)],
        ]
    )


def inventory_search_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[_callback_button("Отменить поиск", InventoryAction.CANCEL_SEARCH)]]
    )


def inventory_compare_keyboard(item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_callback_button("↩️ К предмету", InventoryAction.ITEM, item_id)],
            [_callback_button("↩️ К предметам", InventoryAction.BACK_LIST)],
        ]
    )
