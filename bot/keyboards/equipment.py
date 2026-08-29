from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks.character import CharacterCallback, CharacterSection
from bot.callbacks.equipment import EquipmentAction, EquipmentCallback
from bot.models.equipment import (
    EquipmentGroup,
    EquipmentLoadout,
    EquippedSlot,
)


def _equipment_button(
    text: str,
    action: EquipmentAction,
    value: str = "",
    *,
    style: str | None = None,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=EquipmentCallback(action=action, value=value).pack(),
        style=style,
    )


def _character_button(text: str, section: CharacterSection) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=CharacterCallback(section=section).pack(),
    )


def _group_count(loadout: EquipmentLoadout, group: EquipmentGroup) -> tuple[int, int]:
    slots = tuple(slot for slot in loadout.slots if slot.group is group)
    return sum(slot.occupied for slot in slots), len(slots)


def equipment_keyboard(
    loadout: EquipmentLoadout,
) -> InlineKeyboardMarkup:
    armor = _group_count(loadout, EquipmentGroup.ARMOR)
    weapons = _group_count(loadout, EquipmentGroup.WEAPONS)
    jewelry = _group_count(loadout, EquipmentGroup.JEWELRY)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _equipment_button(
                    f"🛡 Броня · {armor[0]}/{armor[1]}",
                    EquipmentAction.GROUP,
                    EquipmentGroup.ARMOR.value,
                ),
                _equipment_button(
                    f"⚔️ Оружие · {weapons[0]}/{weapons[1]}",
                    EquipmentAction.GROUP,
                    EquipmentGroup.WEAPONS.value,
                ),
            ],
            [
                _equipment_button(
                    f"💍 Украшения · {jewelry[0]}/{jewelry[1]}",
                    EquipmentAction.GROUP,
                    EquipmentGroup.JEWELRY.value,
                ),
            ],
            [
                _character_button("📊 Характеристики", CharacterSection.STATS),
                _character_button("↩️ Персонаж", CharacterSection.OVERVIEW),
            ],
        ]
    )


def equipment_group_keyboard(
    group: EquipmentGroup,
    slots: tuple[EquippedSlot, ...],
) -> InlineKeyboardMarkup:
    slot_buttons = [
        _equipment_button(
            f"{'✅' if slot.occupied else '▫️'} {slot.label}",
            EquipmentAction.SLOT,
            slot.slot_id,
        )
        for slot in slots
    ]
    rows = [slot_buttons[index : index + 2] for index in range(0, len(slot_buttons), 2)]
    rows.append([_equipment_button("↩️ Экипировка", EquipmentAction.HOME)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def equipped_slot_keyboard(slot: EquippedSlot) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _equipment_button(
                    f"↩️ {slot.group.title}",
                    EquipmentAction.GROUP,
                    slot.group.value,
                )
            ],
            [_equipment_button("🛡 Экипировка", EquipmentAction.HOME)],
        ]
    )
