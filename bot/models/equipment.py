from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EquipmentGroup(StrEnum):
    ARMOR = "armor"
    WEAPONS = "weapons"
    JEWELRY = "jewelry"

    @property
    def title(self) -> str:
        return {
            EquipmentGroup.ARMOR: "Броня",
            EquipmentGroup.WEAPONS: "Оружие",
            EquipmentGroup.JEWELRY: "Украшения",
        }[self]

    @property
    def icon(self) -> str:
        return {
            EquipmentGroup.ARMOR: "🛡",
            EquipmentGroup.WEAPONS: "⚔️",
            EquipmentGroup.JEWELRY: "💍",
        }[self]


class EquipmentViewMode(StrEnum):
    ITEMS = "items"
    BONUSES = "bonuses"


@dataclass(frozen=True, slots=True)
class EquippedCard:
    name: str
    rarity: str = "common"


@dataclass(frozen=True, slots=True)
class EquippedSlot:
    slot_id: str
    label: str
    icon: str
    group: EquipmentGroup
    item_name: str = ""
    rarity: str = "empty"
    bonuses: tuple[str, ...] = ()
    enhancement_level: int = 0
    asset_name: str = ""
    card: EquippedCard | None = None

    @property
    def occupied(self) -> bool:
        return bool(self.item_name)

    @property
    def display_name(self) -> str:
        if not self.occupied:
            return "Пусто"
        suffix = f" +{self.enhancement_level}" if self.enhancement_level else ""
        return f"{self.item_name}{suffix}"


@dataclass(frozen=True, slots=True)
class EquipmentLoadout:
    character_name: str
    slots: tuple[EquippedSlot, ...]
    total_bonuses: tuple[str, ...]

    @property
    def occupied_count(self) -> int:
        return sum(slot.occupied for slot in self.slots)
