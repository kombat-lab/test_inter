from __future__ import annotations

from dataclasses import replace
from io import BytesIO

from PIL import Image

from bot.keyboards.equipment import (
    equipment_group_keyboard,
    equipment_keyboard,
    equipped_slot_keyboard,
)
from bot.models.equipment import EquipmentGroup, EquippedCard
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
from bot.views.equipment_image import _font as equipment_font
from bot.views.equipment_image import render_equipment_board


def test_equipment_board_is_generated_from_loadout() -> None:
    loadout = get_equipment_loadout(1)
    items_image = render_equipment_board(loadout)

    with Image.open(BytesIO(items_image)) as image:
        assert image.size == (1600, 1600)
        assert image.format == "JPEG"
    assert len(items_image) < 10 * 1024 * 1024
    assert loadout.occupied_count == 12
    assert len(loadout.slots) == 15


def test_equipment_board_uses_bundled_cyrillic_fonts() -> None:
    regular = equipment_font(24)
    bold = equipment_font(24, bold=True)
    display = equipment_font(24, display=True)

    assert str(getattr(regular, "path", "")).endswith("DejaVuSans.ttf")
    assert str(getattr(bold, "path", "")).endswith("DejaVuSans-Bold.ttf")
    assert str(getattr(display, "path", "")).endswith("DejaVuSerif-Bold.ttf")
    assert regular.getbbox("Экипировка") is not None


def test_each_item_has_one_optional_card_slot() -> None:
    loadout = get_equipment_loadout(1)
    main_hand = next(slot for slot in loadout.slots if slot.slot_id == "main_hand")
    assert main_hand.card is None

    card_loadout = replace(
        loadout,
        slots=tuple(
            replace(slot, card=EquippedCard("Карта тумана", "rare"))
            if slot.slot_id == "main_hand"
            else slot
            for slot in loadout.slots
        ),
    )
    assert render_equipment_board(card_loadout) != render_equipment_board(loadout)


def test_equipment_main_screen_is_compact() -> None:
    loadout = get_equipment_loadout(1)
    caption = render_equipment_caption(loadout)
    keyboard = equipment_keyboard(loadout)

    assert "Экипировка · 12/15" in caption
    assert "Защита 61" in caption
    assert "одну Карту" in caption
    assert len(keyboard.inline_keyboard) == 3
    assert keyboard.inline_keyboard[0][0].text == "🛡 Броня · 8/8"
    assert keyboard.inline_keyboard[0][1].text == "⚔️ Оружие · 2/2"
    assert keyboard.inline_keyboard[1][0].text == "💍 Украшения · 2/5"
    assert len(keyboard.inline_keyboard[1]) == 1


def test_equipment_group_and_slot_navigation() -> None:
    slots = get_group_slots(1, EquipmentGroup.JEWELRY)
    caption = render_equipment_group_caption(EquipmentGroup.JEWELRY, slots)
    keyboard = equipment_group_keyboard(EquipmentGroup.JEWELRY, slots)
    earring = get_equipped_slot(1, "earring_1")
    assert earring is not None

    assert "Украшения · 2/5" in caption
    assert any(button.text == "▫️ Кольцо I" for row in keyboard.inline_keyboard for button in row)
    assert "Серьга дропа" in render_equipped_slot_caption(earring)
    assert "Карта: не установлена" in render_equipped_slot_caption(earring)
    assert equipped_slot_keyboard(earring).inline_keyboard[0][0].callback_data == (
        "equipment:group:jewelry"
    )
