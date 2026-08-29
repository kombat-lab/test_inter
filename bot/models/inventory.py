from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ItemCategory(StrEnum):
    ALL = "all"
    QUEST = "quest"
    EQUIPMENT = "equipment"
    CARDS = "cards"
    RESOURCES = "resources"
    CONSUMABLES = "consumables"

    @property
    def title(self) -> str:
        return {
            ItemCategory.ALL: "Все предметы",
            ItemCategory.QUEST: "Квестовые",
            ItemCategory.EQUIPMENT: "Экипировка",
            ItemCategory.CARDS: "Карты",
            ItemCategory.RESOURCES: "Ресурсы",
            ItemCategory.CONSUMABLES: "Расходники",
        }[self]

    @property
    def icon(self) -> str:
        return {
            ItemCategory.ALL: "🗂",
            ItemCategory.QUEST: "📜",
            ItemCategory.EQUIPMENT: "🛡",
            ItemCategory.CARDS: "🃏",
            ItemCategory.RESOURCES: "⛏",
            ItemCategory.CONSUMABLES: "🧪",
        }[self]


@dataclass(frozen=True, slots=True)
class InventoryItem:
    item_id: str
    icon: str
    name: str
    quantity: int
    category: ItemCategory
    description: str
    rarity: str
    effects: tuple[str, ...] = ()
    comparison: tuple[str, ...] = ()
    usable: bool = False
    equipment_slot: str | None = None
    enhancement_level: int = 0
    required_level: int | None = None
    allowed_classes: tuple[str, ...] = ()
    personal: bool = False
    damage_range: str = ""
    compared_with: str = ""


@dataclass(frozen=True, slots=True)
class InventoryPage:
    items: tuple[InventoryItem, ...]
    page: int
    total_pages: int
    total_items: int
    occupied_slots: int
    capacity: int
