from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from bot.models.equipment import EquipmentLoadout, EquipmentViewMode, EquippedSlot

_CANVAS_SIZE = (1600, 1000)
_CHARACTER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "character.png"
_FONT_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_REGULAR_FONT = _FONT_DIRECTORY / "DejaVuSans.ttf"
_BOLD_FONT = _FONT_DIRECTORY / "DejaVuSans-Bold.ttf"
_RARITY_COLORS = {
    "empty": (82, 96, 110, 210),
    "common": (212, 219, 226, 235),
    "uncommon": (72, 198, 117, 235),
    "rare": (70, 145, 255, 235),
    "epic": (164, 92, 255, 235),
}


@lru_cache(maxsize=16)
def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = _BOLD_FONT if bold else _REGULAR_FONT
    return ImageFont.truetype(font_path, size)


def _truncate(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    max_width: int,
) -> str:
    if draw.textlength(text, font=font) <= max_width:
        return text
    shortened = text
    while shortened and draw.textlength(f"{shortened}…", font=font) > max_width:
        shortened = shortened[:-1]
    return f"{shortened}…"


def _draw_slot(
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
    mode: EquipmentViewMode,
    *,
    connector_x: int,
) -> None:
    x1, y1, x2, y2 = box
    accent = _RARITY_COLORS[slot.rarity]
    center_y = (y1 + y2) // 2
    line_start = x2 if connector_x > x2 else x1
    draw.line((line_start, center_y, connector_x, center_y), fill=(*accent[:3], 115), width=3)
    draw.rounded_rectangle(box, radius=18, fill=(12, 23, 34, 232), outline=accent, width=4)

    label_font = _font(21, bold=True)
    value_font = _font(27, bold=slot.occupied)
    draw.text((x1 + 20, y1 + 12), slot.label.upper(), font=label_font, fill=(151, 167, 184))

    if not slot.occupied:
        value = "— пусто —"
        value_color = (113, 128, 143)
    elif mode is EquipmentViewMode.BONUSES:
        value = " · ".join(slot.bonuses[:3]) or "Без бонусов"
        value_color = accent[:3]
    else:
        value = slot.display_name
        value_color = (239, 244, 249)
    value = _truncate(draw, value, value_font, x2 - x1 - 40)
    draw.text((x1 + 20, y1 + 45), value, font=value_font, fill=value_color)


@lru_cache(maxsize=8)
def render_equipment_board(
    loadout: EquipmentLoadout,
    mode: EquipmentViewMode = EquipmentViewMode.ITEMS,
) -> bytes:
    source = Image.open(_CHARACTER_IMAGE).convert("RGB")
    background = ImageOps.fit(source, _CANVAS_SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(28))
    background = ImageEnhance.Brightness(background).enhance(0.2).convert("RGBA")

    canvas = background
    character = ImageOps.fit(
        source, (620, 900), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45)
    )
    character = ImageEnhance.Contrast(character).enhance(1.05).convert("RGBA")
    mask = Image.new("L", character.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *character.size), radius=34, fill=255)
    canvas.paste(character, (490, 64), mask)

    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((486, 60, 1114, 968), radius=38, outline=(115, 139, 159, 150), width=3)
    draw.rectangle((0, 0, 1600, 66), fill=(5, 12, 19, 220))
    title_font = _font(30, bold=True)
    subtitle_font = _font(21)
    draw.text((800, 14), "ЭКИПИРОВКА", font=title_font, anchor="ma", fill=(240, 244, 248))
    draw.text(
        (800, 48),
        f"{loadout.character_name} · {loadout.occupied_count}/{len(loadout.slots)} слотов",
        font=subtitle_font,
        anchor="ma",
        fill=(164, 181, 197),
    )

    left_slots = loadout.slots[:7]
    right_slots = loadout.slots[7:]
    for index, slot in enumerate(left_slots):
        y = 88 + index * 124
        _draw_slot(draw, slot, (28, y, 466, y + 98), mode, connector_x=500)
    for index, slot in enumerate(right_slots):
        y = 84 + index * 108
        _draw_slot(draw, slot, (1134, y, 1572, y + 86), mode, connector_x=1100)

    output = BytesIO()
    canvas.convert("RGB").save(output, format="JPEG", quality=88, optimize=True)
    return output.getvalue()
