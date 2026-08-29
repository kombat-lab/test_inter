from __future__ import annotations

from html import escape

from bot.models.character import Character
from bot.models.inventory import InventoryItem, InventoryPage, ItemCategory


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def render_inventory_caption(
    inventory: InventoryPage,
    character: Character,
    category: ItemCategory,
    *,
    query: str = "",
) -> str:
    lines = [
        f"🎒 <b>Инвентарь · {inventory.occupied_slots}/{inventory.capacity}</b>",
        f"✨ <b>{_format_number(character.mist_dust)}</b>  ·  "
        f"💎 <b>{_format_number(character.mist_crystals)}</b>",
        "",
    ]
    if query:
        lines.extend(
            [
                f"🔎 <b>{escape(query)}</b> · найдено {inventory.total_items}",
                f"Страница {inventory.page + 1} из {inventory.total_pages}",
            ]
        )
    else:
        lines.extend(
            [
                f"{category.icon} <b>{category.title}</b> · {inventory.total_items}",
                f"Страница {inventory.page + 1} из {inventory.total_pages}",
            ]
        )
    hint = (
        "Нажмите на предмет, чтобы открыть его."
        if inventory.total_items
        else "Ничего не найдено. Измените поиск или категорию."
    )
    lines.extend(["", f"<i>{hint}</i>"])
    return "\n".join(lines)


def render_filter_caption(current: ItemCategory) -> str:
    return (
        "🗂 <b>Категория инвентаря</b>\n\n"
        f"Сейчас выбрано: {current.icon} <b>{current.title}</b>\n"
        "Выберите раздел:"
    )


def render_search_prompt() -> str:
    return (
        "🔎 <b>Поиск предметов</b>\n\n"
        "Отправьте часть названия предмета одним сообщением.\n"
        "Например: <code>яд</code>, <code>кожа</code> или <code>туман</code>."
    )


def render_item_caption(item: InventoryItem, *, equipped: bool = False, notice: str = "") -> str:
    lines = [
        f"{escape(item.icon)} <b>{escape(item.name)}</b>",
        f"{item.category.icon} {item.category.title} · <b>{item.quantity} шт.</b>",
        "",
        escape(item.description),
        "",
        f"Редкость: <b>{escape(item.rarity)}</b>",
    ]
    if item.equipment_slot:
        lines.extend(
            [
                f"Слот: <b>{escape(item.equipment_slot)}</b>",
                f"Состояние: <b>{'экипировано' if equipped else 'в рюкзаке'}</b>",
            ]
        )
    if item.effects:
        lines.extend(["", "<b>Свойства</b>"])
        lines.extend(f"• {escape(effect)}" for effect in item.effects)
    if notice:
        lines.extend(["", f"✅ <i>{escape(notice)}</i>"])
    return "\n".join(lines)


def render_compare_caption(item: InventoryItem, *, equipped: bool) -> str:
    state = "сейчас экипирован" if equipped else "находится в рюкзаке"
    comparison = "\n".join(f"• {escape(line)}" for line in item.comparison)
    return (
        f"⚖️ <b>Сравнение: {escape(item.name)}</b>\n\n"
        f"Предмет {state}.\n"
        f"Слот: <b>{escape(item.equipment_slot or '—')}</b>\n\n"
        f"<b>Относительно надетого предмета</b>\n"
        f"{comparison or '• Сравнение пока недоступно'}"
    )
