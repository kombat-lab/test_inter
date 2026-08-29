from __future__ import annotations

from html import escape

from bot.models.equipment import (
    EquipmentGroup,
    EquipmentLoadout,
    EquipmentViewMode,
    EquippedSlot,
)


def render_equipment_caption(
    loadout: EquipmentLoadout,
    mode: EquipmentViewMode,
) -> str:
    mode_title = "названия предметов" if mode is EquipmentViewMode.ITEMS else "бонусы предметов"
    bonuses = loadout.total_bonuses
    return "\n".join(
        [
            f"🛡 <b>Экипировка · {loadout.occupied_count}/{len(loadout.slots)}</b>",
            f"<i>На изображении: {mode_title}</i>",
            "",
            "<b>Итоговые показатели</b>",
            f"{bonuses[0]}  ·  {bonuses[2]}  ·  {bonuses[3]}",
            f"{bonuses[1]}  ·  {bonuses[4]}",
            f"{bonuses[5]}  ·  {bonuses[6]}",
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
    return "\n".join(
        [
            f"{escape(slot.icon)} <b>{escape(slot.label)}</b>",
            f"<b>{escape(slot.display_name)}</b>",
            "",
            "<b>Бонусы предмета</b>",
            bonuses or "• Нет бонусов",
        ]
    )
