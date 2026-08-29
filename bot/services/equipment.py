from __future__ import annotations

from bot.models.equipment import EquipmentGroup, EquipmentLoadout, EquippedSlot

_SLOTS = (
    EquippedSlot(
        "head",
        "Шлем",
        "🪖",
        EquipmentGroup.ARMOR,
        "Помятый шлем",
        "common",
        ("Инт +3", "Вын +2", "Защ +11", "Ид. крит +1"),
    ),
    EquippedSlot(
        "shoulders",
        "Плечи",
        "🧥",
        EquipmentGroup.ARMOR,
        "Ржавый наплечник",
        "common",
        ("Инт +2", "Вын +2"),
    ),
    EquippedSlot(
        "body",
        "Тело",
        "👕",
        EquipmentGroup.ARMOR,
        "Чешуйчатый нагрудник",
        "uncommon",
        ("Инт +5", "Уда +1", "Защ +18"),
    ),
    EquippedSlot(
        "cloak",
        "Плащ",
        "🧣",
        EquipmentGroup.ARMOR,
        "Плащ из плотной ткани",
        "common",
        ("Вын +3", "Скор +15%"),
    ),
    EquippedSlot("belt", "Пояс", "🪢", EquipmentGroup.ARMOR),
    EquippedSlot(
        "pants",
        "Штаны",
        "👖",
        EquipmentGroup.ARMOR,
        "Плотные штаны",
        "rare",
        ("Вын +3", "Уда +1", "Защ +9", "Маг. защ +5"),
        3,
    ),
    EquippedSlot(
        "boots",
        "Ботинки",
        "🥾",
        EquipmentGroup.ARMOR,
        "Тяжёлые ботинки",
        "rare",
        ("Инт +1", "Вын +1", "Уда +1", "Защ +1", "Маг. защ +7"),
    ),
    EquippedSlot(
        "gloves",
        "Перчатки",
        "🧤",
        EquipmentGroup.ARMOR,
        "Костяные браслеты",
        "rare",
        ("Инт +2", "Вын +5", "Уда +1", "Защ +11", "Маг. защ +5", "Крит +1%"),
        4,
    ),
    EquippedSlot("ring_1", "Кольцо I", "💍", EquipmentGroup.JEWELRY),
    EquippedSlot("ring_2", "Кольцо II", "💍", EquipmentGroup.JEWELRY),
    EquippedSlot("amulet", "Амулет", "📿", EquipmentGroup.JEWELRY),
    EquippedSlot(
        "earring_1",
        "Серьга I",
        "📎",
        EquipmentGroup.JEWELRY,
        "Серьга дропа (30 дней)",
        "epic",
        ("Лут +15%",),
    ),
    EquippedSlot(
        "earring_2",
        "Серьга II",
        "📎",
        EquipmentGroup.JEWELRY,
        "Серьга дропа (30 дней)",
        "epic",
        ("Лут +15%",),
    ),
    EquippedSlot(
        "main_hand",
        "Основная рука",
        "🪄",
        EquipmentGroup.WEAPONS,
        "Витой тотем",
        "rare",
        ("Инт +2", "Вын +5", "Уда +1"),
        6,
    ),
    EquippedSlot(
        "off_hand",
        "Вторая рука",
        "🛡",
        EquipmentGroup.WEAPONS,
        "Башенный щит",
        "rare",
        ("Инт +1", "Вын +3", "Защ +7", "Маг. защ +12", "Блок +8%"),
    ),
)

_TOTAL_BONUSES = (
    "❤️ HP 750",
    "🐾 Скорость +15%",
    "🛡 Защита 61",
    "🪬 Маг. защита 58",
    "💢 Крит 3",
    "🔮 Маг. атака 67",
    "🧱 Блок 8",
)


def get_equipment_loadout(_user_id: int) -> EquipmentLoadout:
    """Return reference equipment until persistent player storage is connected."""
    return EquipmentLoadout("Kombat", _SLOTS, _TOTAL_BONUSES)


def get_equipped_slot(user_id: int, slot_id: str) -> EquippedSlot | None:
    return next(
        (slot for slot in get_equipment_loadout(user_id).slots if slot.slot_id == slot_id),
        None,
    )


def get_group_slots(user_id: int, group: EquipmentGroup) -> tuple[EquippedSlot, ...]:
    return tuple(slot for slot in get_equipment_loadout(user_id).slots if slot.group is group)
