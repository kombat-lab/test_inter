from __future__ import annotations

from bot.models.equipment import EquipmentGroup, EquipmentLoadout, EquippedSlot

_SLOTS = (
    EquippedSlot(
        slot_id="head",
        label="Шлем",
        icon="🪖",
        group=EquipmentGroup.ARMOR,
        item_name="Помятый шлем",
        rarity="common",
        bonuses=("Инт +3", "Вын +2", "Защ +11", "Маг. защ +1"),
        asset_name="head.png",
    ),
    EquippedSlot(
        slot_id="shoulders",
        label="Плечи",
        icon="🪹",
        group=EquipmentGroup.ARMOR,
        item_name="Ржавый наплечник",
        rarity="common",
        bonuses=("Инт +2", "Вын +2"),
        asset_name="shoulders.png",
    ),
    EquippedSlot(
        slot_id="body",
        label="Тело",
        icon="👕",
        group=EquipmentGroup.ARMOR,
        item_name="Чешуйчатый нагрудник",
        rarity="uncommon",
        bonuses=("Инт +5", "Уда +1", "Защ +18"),
        asset_name="body.png",
    ),
    EquippedSlot(
        slot_id="cloak",
        label="Плащ",
        icon="🧣",
        group=EquipmentGroup.ARMOR,
        item_name="Плащ из плотной ткани",
        rarity="common",
        bonuses=("Вын +3", "Скор +15%"),
        asset_name="cloak.png",
    ),
    EquippedSlot(
        slot_id="belt",
        label="Пояс",
        icon="🪢",
        group=EquipmentGroup.ARMOR,
        item_name="Пояс из чешуи",
        rarity="common",
        bonuses=("Вын +1",),
        asset_name="belt.png",
    ),
    EquippedSlot(
        slot_id="pants",
        label="Штаны",
        icon="🩳",
        group=EquipmentGroup.ARMOR,
        item_name="Плотные штаны",
        rarity="rare",
        bonuses=("Вын +3", "Уда +1", "Защ +9", "Маг. защ +5"),
        enhancement_level=3,
        asset_name="pants.png",
    ),
    EquippedSlot(
        slot_id="boots",
        label="Ботинки",
        icon="🥾",
        group=EquipmentGroup.ARMOR,
        item_name="Тяжёлые ботинки",
        rarity="rare",
        bonuses=("Инт +1", "Вын +1", "Уда +1", "Защ +1", "Маг. защ +7"),
        asset_name="boots.png",
    ),
    EquippedSlot(
        slot_id="gloves",
        label="Перчатки",
        icon="🧤",
        group=EquipmentGroup.ARMOR,
        item_name="Костяные браслеты",
        rarity="rare",
        bonuses=(
            "Инт +2",
            "Вын +5",
            "Уда +1",
            "Защ +11",
            "Маг. защ +5",
            "Сила крита +1%",
            "Крит +5%",
        ),
        enhancement_level=4,
        asset_name="gloves.png",
    ),
    EquippedSlot(
        slot_id="ring_1", label="Кольцо I", icon="💍", group=EquipmentGroup.JEWELRY
    ),
    EquippedSlot(
        slot_id="ring_2", label="Кольцо II", icon="💍", group=EquipmentGroup.JEWELRY
    ),
    EquippedSlot(slot_id="amulet", label="Амулет", icon="📿", group=EquipmentGroup.JEWELRY),
    EquippedSlot(
        slot_id="earring_1",
        label="Серьга I",
        icon="🧷",
        group=EquipmentGroup.JEWELRY,
        item_name="Серьга дропа (30 дней)",
        rarity="epic",
        bonuses=("Лут +15%",),
        asset_name="earring.png",
    ),
    EquippedSlot(
        slot_id="earring_2",
        label="Серьга II",
        icon="🧷",
        group=EquipmentGroup.JEWELRY,
        item_name="Серьга дропа (30 дней)",
        rarity="epic",
        bonuses=("Лут +15%",),
        asset_name="earring.png",
    ),
    EquippedSlot(
        slot_id="main_hand",
        label="Основная рука",
        icon="🗡️",
        group=EquipmentGroup.WEAPONS,
        item_name="Витой тотем",
        rarity="rare",
        bonuses=("Инт +2", "Вын +5", "Уда +1"),
        enhancement_level=2,
        asset_name="main_hand.png",
    ),
    EquippedSlot(
        slot_id="off_hand",
        label="Вторая рука",
        icon="🛡",
        group=EquipmentGroup.WEAPONS,
        item_name="Башенный щит",
        rarity="rare",
        bonuses=("Инт +1", "Вын +3", "Защ +7", "Маг. защ +12", "Блок +8%"),
        asset_name="off_hand.png",
    ),
)

_TOTAL_BONUSES = (
    "❤️ HP 750",
    "🐾 Скорость +15%",
    "❤️ Бонус HP от экипа +0",
    "🐾 Бонус скорости от экипа +15%",
    "🛡 Защита 61",
    "🪬 Маг. защита 58",
    "💢 Крит 3",
    "⚔️ Атака 1",
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
