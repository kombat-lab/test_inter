from __future__ import annotations

from html import escape

from bot.models.equipment import (
    EquipmentGroup,
    EquipmentLoadout,
    EquippedSlot,
)


def render_equipment_caption(
    loadout: EquipmentLoadout,
) -> str:
    bonuses = loadout.total_bonuses
    return "\n".join(
        [
            f"🛡 <b>Экипировка · {loadout.occupied_count}/{len(loadout.slots)}</b>",
            "<i>Характеристики, заточка и установленные Карты показаны на изображении.</i>",
            "🃏 В каждую вещь можно вставить одну Карту.",
            "",
            "<b>Итоговые показатели</b>",
            "  ·  ".join(bonuses[:5]),
            "  ·  ".join(bonuses[5:]),
            "",
            "<i>Выберите группу снаряжения.</i>",
        ]
    )


def render_equipment_group_caption(
    group: EquipmentGroup,
    slots: tuple[EquippedSlot, ...],
) -> str:
    occupied = sum(slot.occupied for slot in slots)
    return (
        f"{group.icon} <b>{group.title} · {occupied}/{len(slots)}</b>\n\n"
        "Выберите слот. Занятые слоты отмечены цветом редкости, "
        "пустые — серым."
    )


def render_equipped_slot_caption(slot: EquippedSlot) -> str:
    if not slot.occupied:
        return f"{escape(slot.icon)} <b>{escape(slot.label)}</b>\n\n▫️ Слот свободен."

    bonuses = "\n".join(f"• {escape(bonus)}" for bonus in slot.bonuses)
    enhancement = f"Заточка: <b>+{slot.enhancement_level}</b>" if slot.enhancement_level else ""
    card = (
        f"🃏 Карта: <b>{escape(slot.card.name)}</b>"
        if slot.card is not None
        else "🃏 Карта: не установлена"
    )
    return "\n".join(
        [
            f"{escape(slot.icon)} <b>{escape(slot.label)}</b>",
            f"<b>{escape(slot.display_name)}</b>",
            enhancement,
            card,
            "",
            "<b>Бонусы предмета</b>",
            bonuses or "• Нет бонусов",
        ]
    )
