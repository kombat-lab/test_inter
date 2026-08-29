from __future__ import annotations

from io import BytesIO

from PIL import Image

from bot.keyboards.equipment import (
    equipment_group_keyboard,
    equipment_keyboard,
    equipped_slot_keyboard,
)
from bot.models.equipment import EquipmentGroup, EquipmentViewMode
from bot.services.equipment import (
    get_equipment_loadout,
    get_equipped_slot,
    get_group_slots,
)
from bot.views.equipment import (
    render_equipment_caption,
    render_equipment_group_caption,
    render_equipped_slot_caption,
)
from bot.views.equipment_image import render_equipment_board


def test_equipment_board_is_generated_from_loadout() -> None:
    loadout = get_equipment_loadout(1)
    items_image = render_equipment_board(loadout, EquipmentViewMode.ITEMS)
    bonuses_image = render_equipment_board(loadout, EquipmentViewMode.BONUSES)

    with Image.open(BytesIO(items_image)) as image:
        assert image.size == (1600, 1000)
        assert image.format == "JPEG"
    assert len(items_image) < 10 * 1024 * 1024
    assert items_image != bonuses_image
    assert loadout.occupied_count == 11
    assert len(loadout.slots) == 15


def test_equipment_main_screen_is_compact() -> None:
    loadout = get_equipment_loadout(1)
    caption = render_equipment_caption(loadout, EquipmentViewMode.ITEMS)
    keyboard = equipment_keyboard(loadout, EquipmentViewMode.ITEMS)

    assert "Экипировка · 11/15" in caption
    assert "Защита 61" in caption
    assert len(keyboard.inline_keyboard) == 3
    assert keyboard.inline_keyboard[0][0].text == "🛡 Броня · 7/8"
    assert keyboard.inline_keyboard[0][1].text == "⚔️ Оружие · 2/2"
    assert keyboard.inline_keyboard[1][0].text == "💍 Украшения · 2/5"
    assert keyboard.inline_keyboard[1][1].text == "📊 Показать бонусы"


def test_equipment_group_and_slot_navigation() -> None:
    slots = get_group_slots(1, EquipmentGroup.JEWELRY)
    caption = render_equipment_group_caption(EquipmentGroup.JEWELRY, slots)
    keyboard = equipment_group_keyboard(EquipmentGroup.JEWELRY, slots)
    earring = get_equipped_slot(1, "earring_1")
    assert earring is not None

    assert "Украшения · 2/5" in caption
    assert any(button.text == "▫️ Кольцо I" for row in keyboard.inline_keyboard for button in row)
    assert "Серьга дропа" in render_equipped_slot_caption(earring)
    assert equipped_slot_keyboard(earring).inline_keyboard[0][0].callback_data == (
        "equipment:group:jewelry"
    )
