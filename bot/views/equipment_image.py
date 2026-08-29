from __future__ import annotations

import re
from functools import lru_cache
from io import BytesIO
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from bot.models.equipment import EquipmentLoadout, EquippedSlot

_CANVAS_SIZE = (1600, 1600)
_ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets"
_EQUIPMENT_ASSET_DIRECTORY = _ASSET_DIRECTORY / "equipment"
_STAT_ICON_DIRECTORY = _ASSET_DIRECTORY / "stat_icons"
_UI_BASE = _ASSET_DIRECTORY / "ui" / "equipment-fog-clean-v3.png"
_CHARACTER_IMAGE = _ASSET_DIRECTORY / "character.png"
_FONT_DIRECTORY = _ASSET_DIRECTORY / "fonts"
_TEXT_FONT = _FONT_DIRECTORY / "Oswald-Variable.ttf"

_RARITY_COLORS = {
    "empty": (103, 109, 111),
    "common": (204, 202, 194),
    "uncommon": (48, 211, 85),
    "rare": (38, 145, 244),
    "epic": (179, 58, 240),
}
_CARD_COLORS = {
    "common": (201, 202, 195),
    "uncommon": (68, 204, 91),
    "rare": (53, 142, 239),
    "epic": (176, 66, 230),
}
_LEFT_SLOT_IDS = ("head", "shoulders", "body", "cloak", "belt", "pants", "boots", "gloves")
_RIGHT_SLOT_IDS = (
    "earring_1",
    "earring_2",
    "ring_1",
    "ring_2",
    "amulet",
    "main_hand",
    "off_hand",
)
_BONUS_PREFIXES = (
    ("Сила крита", "critical_power"),
    ("Маг. защ", "magic_defense"),
    ("Инт", "intelligence"),
    ("Вын", "regeneration"),
    ("Уда", "luck"),
    ("Защ", "defense"),
    ("Крит", "critical"),
    ("Лут", "drop"),
    ("Скор", "speed"),
    ("Блок", "block"),
)
_STAT_ICON_FILES = {
    "hp": "hp.png",
    "attack": "damage.png",
    "intelligence": "intelligence.png",
    "regeneration": "endurance.png",
    "endurance": "endurance.png",
    "defense": "defense.png",
    "magic_defense": "magic_defense.png",
    "luck": "luck.png",
    "critical_power": "critical_power.png",
    "critical": "critical.png",
    "drop": "drop.png",
    "speed": "speed.png",
    "block": "block.png",
    "magic_attack": "magic_attack.png",
}


@lru_cache(maxsize=48)
def _font(
    size: int,
    *,
    bold: bool = False,
    display: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font = ImageFont.truetype(_TEXT_FONT, size)
    try:
        weight = 720 if display else (650 if bold else 470)
        font.set_variation_by_axes([weight])
    except (AttributeError, OSError):
        pass
    return font


@lru_cache(maxsize=32)
def _source_image(path: str) -> Image.Image:
    with Image.open(path) as source:
        return source.convert("RGB")


@lru_cache(maxsize=32)
def _source_rgba(path: str) -> Image.Image:
    with Image.open(path) as source:
        return source.convert("RGBA")


def _chamfered_points(
    box: tuple[int, int, int, int], cut: int
) -> tuple[tuple[int, int], ...]:
    x1, y1, x2, y2 = box
    return (
        (x1 + cut, y1),
        (x2 - cut, y1),
        (x2, y1 + cut),
        (x2, y2 - cut),
        (x2 - cut, y2),
        (x1 + cut, y2),
        (x1, y2 - cut),
        (x1, y1 + cut),
    )


def _inset(box: tuple[int, int, int, int], amount: int) -> tuple[int, int, int, int]:
    x1, y1, x2, y2 = box
    return x1 + amount, y1 + amount, x2 - amount, y2 - amount


def _draw_chamfered_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    border: tuple[int, int, int],
    fill: tuple[int, int, int, int] = (5, 10, 14, 238),
    cut: int = 12,
    width: int = 3,
) -> None:
    points = _chamfered_points(box, cut)
    draw.polygon(points, fill=fill)
    draw.line((*points, points[0]), fill=(*border, 245), width=width, joint="curve")
    inner_box = _inset(box, width + 3)
    inner = _chamfered_points(inner_box, max(4, cut - width - 1))
    draw.line((*inner, inner[0]), fill=(225, 231, 226, 42), width=1)
    x1, y1, x2, _ = box
    draw.line(
        (x1 + cut + 5, y1 + width + 1, x2 - cut - 5, y1 + width + 1),
        fill=(245, 247, 240, 35),
        width=1,
    )


def _add_glow(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
) -> None:
    if color == _RARITY_COLORS["common"]:
        return
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer, "RGBA")
    points = _chamfered_points(box, 12)
    layer_draw.line((*points, points[0]), fill=(*color, 135), width=7)
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(14)))


def _background() -> Image.Image:
    foundation = _source_image(str(_UI_BASE))
    return ImageOps.fit(
        foundation,
        _CANVAS_SIZE,
        method=Image.Resampling.LANCZOS,
    ).convert("RGBA")


def _paste_character(canvas: Image.Image) -> None:
    character = _source_image(str(_CHARACTER_IMAGE))
    target = (405, 73, 1195, 1390)
    width = target[2] - target[0]
    height = target[3] - target[1]
    fitted = ImageOps.fit(
        character,
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.49),
    ).convert("RGBA")
    fitted = ImageEnhance.Contrast(fitted).enhance(1.07)
    fitted = ImageEnhance.Color(fitted).enhance(0.72)

    mask = Image.new("L", fitted.size, 255)
    mask_draw = ImageDraw.Draw(mask)
    fade = 38
    for offset in range(fade):
        alpha = int(255 * offset / fade)
        mask_draw.line((offset, 0, offset, height), fill=alpha)
        mask_draw.line((width - offset - 1, 0, width - offset - 1, height), fill=alpha)
    for y in range(height - 130, height):
        alpha = int(255 * (height - y) / 130)
        mask_draw.line((0, y, width, y), fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    canvas.paste(fitted, (target[0], target[1]), mask)

    fog = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog, "RGBA")
    fog_draw.ellipse((335, 850, 1260, 1490), fill=(142, 154, 157, 30))
    canvas.alpha_composite(fog.filter(ImageFilter.GaussianBlur(75)))


def _star_points(
    center: tuple[int, int], outer: int, inner: int, points: int = 8
) -> tuple[tuple[float, float], ...]:
    x, y = center
    vertices = []
    for index in range(points * 2):
        radius = outer if index % 2 == 0 else inner
        angle = -pi / 2 + index * pi / points
        vertices.append((x + cos(angle) * radius, y + sin(angle) * radius))
    return tuple(vertices)


def _draw_stat_icon(
    draw: ImageDraw.ImageDraw,
    key: str,
    center: tuple[int, int],
    size: int = 12,
) -> None:
    x, y = center
    shadow = (0, 0, 0, 170)
    if key == "intelligence":
        color = (239, 229, 205, 255)
        draw.ellipse((x - 11, y - 12, x + 11, y + 12), fill=shadow)
        for dx, dy in ((-5, -5), (4, -6), (-6, 4), (5, 5)):
            draw.ellipse((x + dx - 6, y + dy - 6, x + dx + 6, y + dy + 6), fill=color)
        draw.line((x, y - 10, x, y + 10), fill=(111, 91, 78, 180), width=2)
        draw.arc((x - 9, y - 4, x + 1, y + 7), 255, 75, fill=(111, 91, 78), width=2)
    elif key == "regeneration":
        color = (244, 229, 213, 255)
        draw.ellipse((x - 12, y - 10, x, y + 3), fill=color)
        draw.ellipse((x, y - 10, x + 12, y + 3), fill=color)
        draw.polygon(((x - 12, y - 3), (x + 12, y - 3), (x, y + 14)), fill=color)
        draw.line((x - 5, y - 2, x + 5, y + 7), fill=(204, 165, 154), width=2)
    elif key == "luck":
        color = (202, 211, 102, 255)
        for dx, dy in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
            draw.ellipse((x + dx - 6, y + dy - 6, x + dx + 6, y + dy + 6), fill=color)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(96, 112, 46, 255))
        draw.line((x + 3, y + 6, x + 10, y + 15), fill=color, width=3)
    elif key == "defense":
        color = (225, 225, 205, 255)
        draw.polygon(
            (
                (x, y - 14),
                (x + 12, y - 8),
                (x + 9, y + 8),
                (x, y + 15),
                (x - 9, y + 8),
                (x - 12, y - 8),
            ),
            fill=color,
        )
        draw.line((x, y - 10, x, y + 10), fill=(87, 112, 121), width=3)
        draw.line((x - 7, y - 5, x + 7, y - 5), fill=(87, 112, 121), width=2)
    elif key == "magic_defense":
        color = (226, 215, 170, 255)
        draw.ellipse((x - 13, y - 13, x + 13, y + 13), outline=shadow, width=5)
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), outline=color, width=3)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(52, 135, 220, 255))
        draw.ellipse((x - 2, y - 3, x + 1, y), fill=(230, 246, 255, 240))
    elif key == "critical_power":
        draw.polygon(_star_points(center, size + 3, 5, 9), fill=(245, 137, 55, 255))
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(255, 219, 129, 255))
    elif key == "critical":
        draw.polygon(_star_points(center, size + 2, 7, 4), fill=(225, 53, 59, 255))
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(49, 13, 17, 255))
    elif key == "drop":
        color = (229, 217, 187, 255)
        draw.rounded_rectangle((x - 13, y - 13, x + 13, y + 13), radius=4, fill=color)
        for dx, dy in ((-6, -6), (6, 6), (-6, 6), (6, -6), (0, 0)):
            draw.ellipse(
                (x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2),
                fill=(67, 52, 42),
            )
    elif key == "speed":
        color = (231, 218, 181, 255)
        draw.ellipse((x - 9, y + 1, x + 9, y + 14), fill=color)
        for dx, dy in ((-11, -7), (-4, -12), (5, -11), (12, -6)):
            draw.ellipse((x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4), fill=color)
    elif key == "block":
        color = (157, 104, 68, 255)
        draw.rectangle((x - 14, y - 10, x + 14, y + 11), fill=color)
        draw.line((x - 14, y, x + 14, y), fill=(59, 37, 28), width=2)
        draw.line((x, y - 10, x, y), fill=(59, 37, 28), width=2)
        draw.line((x - 7, y, x - 7, y + 11), fill=(59, 37, 28), width=2)
        draw.line((x + 7, y, x + 7, y + 11), fill=(59, 37, 28), width=2)
    elif key == "hp":
        _draw_stat_icon(draw, "regeneration", center, size)
        draw.line((x - 6, y + 1, x + 6, y + 1), fill=(223, 45, 51), width=3)
        draw.line((x, y - 5, x, y + 7), fill=(223, 45, 51), width=3)
    elif key == "attack":
        color = (218, 217, 204, 255)
        draw.line((x - 9, y + 11, x + 9, y - 11), fill=shadow, width=7)
        draw.line((x - 9, y + 11, x + 9, y - 11), fill=color, width=4)
        draw.line((x - 11, y - 1, x + 1, y + 11), fill=color, width=3)
    elif key == "magic_attack":
        draw.ellipse(
            (x - 14, y - 14, x + 14, y + 14),
            fill=(32, 22, 49),
            outline=(216, 205, 237),
            width=2,
        )
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(92, 57, 165))
        draw.ellipse((x - 5, y - 7, x + 2, y), fill=(232, 231, 255, 220))


def _paste_stat_icon(
    canvas: Image.Image,
    key: str,
    center: tuple[int, int],
    size: int,
) -> None:
    filename = _STAT_ICON_FILES.get(key, _STAT_ICON_FILES["intelligence"])
    source = _source_rgba(str(_STAT_ICON_DIRECTORY / filename))
    icon = source.resize((size, size), Image.Resampling.LANCZOS)
    x = center[0] - size // 2
    y = center[1] - size // 2

    shadow = Image.new("RGBA", icon.size, (0, 0, 0, 0))
    shadow.putalpha(icon.getchannel("A").filter(ImageFilter.GaussianBlur(3)))
    dark = Image.new("RGBA", icon.size, (0, 0, 0, 155))
    dark.putalpha(shadow.getchannel("A"))
    canvas.alpha_composite(dark, (x + 2, y + 3))
    canvas.alpha_composite(icon, (x, y))


def _draw_lock(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    x, y = origin
    draw.arc((x - 8, y - 10, x + 8, y + 8), 180, 360, fill=(255, 217, 118), width=4)
    draw.rounded_rectangle((x - 10, y, x + 10, y + 18), radius=3, fill=(240, 196, 76))
    draw.ellipse((x - 2, y + 6, x + 2, y + 10), fill=(60, 43, 26))


def _draw_card_socket(
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    center: tuple[int, int],
) -> None:
    x, y = center
    color = (
        (113, 119, 117)
        if slot.card is None
        else _CARD_COLORS.get(slot.card.rarity, _CARD_COLORS["common"])
    )
    box = (x - 17, y - 17, x + 17, y + 17)
    draw.rectangle(
        (x - 20, y - 20, x + 20, y + 20),
        fill=(2, 5, 8, 235),
        outline=(46, 51, 52),
        width=2,
    )
    draw.rectangle(box, fill=(8, 13, 16, 245), outline=(*color, 255), width=3)
    draw.polygon(
        ((x, y - 7), (x + 7, y), (x, y + 7), (x - 7, y)),
        outline=(*color, 220),
    )
    if slot.card is not None:
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*color, 255))


def _item_art(slot: EquippedSlot) -> Image.Image | None:
    if not slot.asset_name:
        return None
    path = _EQUIPMENT_ASSET_DIRECTORY / slot.asset_name
    return _source_image(str(path)) if path.exists() else None


def _paste_item_art(
    canvas: Image.Image,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
) -> None:
    source = _item_art(slot)
    if source is None:
        return
    x1, y1, x2, y2 = box
    art = ImageOps.fit(
        source,
        (x2 - x1, y2 - y1),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.46),
    )
    art = ImageEnhance.Color(art).enhance(0.78)
    art = ImageEnhance.Contrast(art).enhance(1.12).convert("RGBA")
    mask = Image.new("L", art.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(_chamfered_points((0, 0, art.width - 1, art.height - 1), 8), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    canvas.paste(art, (x1, y1), mask)


def _draw_empty_item(
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    metal = (76, 84, 89, 230)
    highlight = (133, 142, 143, 170)
    if slot.slot_id.startswith("ring"):
        draw.ellipse((cx - 33, cy - 32, cx + 33, cy + 34), outline=metal, width=9)
        draw.arc((cx - 29, cy - 28, cx + 29, cy + 30), 200, 330, fill=highlight, width=2)
        draw.polygon(
            ((cx, cy - 48), (cx + 14, cy - 34), (cx, cy - 24), (cx - 14, cy - 34)),
            outline=metal,
            width=3,
        )
    else:
        draw.arc((cx - 46, cy - 47, cx + 46, cy + 25), 20, 160, fill=metal, width=4)
        draw.line((cx - 29, cy - 24, cx - 8, cy + 18), fill=metal, width=3)
        draw.line((cx + 29, cy - 24, cx + 8, cy + 18), fill=metal, width=3)
        draw.polygon(
            ((cx, cy), (cx + 19, cy + 24), (cx, cy + 55), (cx - 19, cy + 24)),
            outline=highlight,
            width=3,
        )


def _bonus_parts(bonus: str) -> tuple[str, str]:
    for prefix, key in _BONUS_PREFIXES:
        if bonus.startswith(prefix):
            return key, bonus[len(prefix) :].strip()
    return "intelligence", bonus


def _draw_bonus_grid(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    if not slot.occupied:
        draw.text(
            ((x1 + x2) // 2, (y1 + y2) // 2),
            "ПУСТО",
            font=_font(26, bold=True),
            anchor="mm",
            fill=(121, 126, 126),
        )
        return
    rows = max(1, (len(slot.bonuses) + 1) // 2)
    row_height = min(34, (y2 - y1 - 18) // rows)
    top = (y1 + y2 - rows * row_height) // 2
    column_width = (x2 - x1 - 18) // 2
    for index, bonus in enumerate(slot.bonuses):
        column = index % 2
        row = index // 2
        x = x1 + 12 + column * column_width
        y = top + row * row_height + row_height // 2
        icon, value = _bonus_parts(bonus)
        _paste_stat_icon(canvas, icon, (x + 14, y), 28)
        draw.text(
            (x + 34, y - 1),
            value,
            font=_font(25, bold=True),
            anchor="lm",
            fill=(112, 240, 116),
            stroke_width=1,
            stroke_fill=(10, 25, 13),
        )


def _draw_equipment_slot(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    item_box: tuple[int, int, int, int],
    stat_box: tuple[int, int, int, int],
) -> None:
    rarity = _RARITY_COLORS.get(slot.rarity, _RARITY_COLORS["common"])
    _add_glow(canvas, item_box, rarity)
    _draw_chamfered_panel(draw, item_box, border=rarity, cut=12, width=4)
    _draw_chamfered_panel(draw, stat_box, border=(118, 118, 112), cut=11, width=2)
    art_box = _inset(item_box, 7)
    if slot.occupied:
        _paste_item_art(canvas, slot, art_box)
        _draw_lock(draw, (item_box[2] - 20, item_box[1] + 17))
        if slot.enhancement_level:
            draw.text(
                (item_box[0] + 12, item_box[1] + 8),
                f"+{slot.enhancement_level}",
                font=_font(27, bold=True),
                fill=(227, 228, 236),
                stroke_width=2,
                stroke_fill=(7, 10, 14),
            )
        _draw_card_socket(
            draw,
            slot,
            ((item_box[0] + item_box[2]) // 2, item_box[3] - 10),
        )
    else:
        _draw_empty_item(draw, slot, art_box)
    _draw_bonus_grid(canvas, draw, slot, stat_box)


def _clean_total(raw: str) -> tuple[str, str]:
    text = raw.strip()
    while text and not text[0].isalnum():
        text = text[1:].lstrip()
    match = re.search(r"([+-]?\d+(?:[.,]\d+)?%?)$", text)
    if not match:
        return text.upper(), ""
    value = match.group(1)
    label = text[: match.start()].strip()
    return label, value


def _fit_font(
    text: str, max_width: int, start: int, *, bold: bool = True
) -> ImageFont.ImageFont:
    for size in range(start, 17, -1):
        font = _font(size, bold=bold)
        if font.getlength(text) <= max_width:
            return font
    return _font(17, bold=bold)


def _sum_item_bonus(loadout: EquipmentLoadout, prefix: str) -> int:
    total = 0
    pattern = re.compile(rf"^{re.escape(prefix)}\s+([+-]?\d+)")
    for slot in loadout.slots:
        for bonus in slot.bonuses:
            match = pattern.match(bonus)
            if match:
                total += int(match.group(1))
    return total


def _bottom_stats(loadout: EquipmentLoadout) -> tuple[tuple[str, str, str], ...]:
    values = {}
    for raw in loadout.total_bonuses:
        raw_label, value = _clean_total(raw)
        values[raw_label] = value
    return (
        ("HP", values.get("HP", "0"), "hp"),
        ("УРОН", values.get("Атака", "0"), "attack"),
        ("ИНТЕЛЛЕКТ", str(_sum_item_bonus(loadout, "Инт")), "intelligence"),
        ("ВЫНОСЛИВОСТЬ", str(_sum_item_bonus(loadout, "Вын")), "endurance"),
        ("ФИЗ. ЗАЩИТА", values.get("Защита", "0"), "defense"),
        ("МАГ. ЗАЩИТА", values.get("Маг. защита", "0"), "magic_defense"),
    )


def _draw_totals(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    loadout: EquipmentLoadout,
) -> None:
    panel = (42, 1430, 1558, 1582)
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.line(
        (*_chamfered_points(panel, 17), _chamfered_points(panel, 17)[0]),
        fill=(115, 142, 148, 85),
        width=8,
    )
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(15)))
    _draw_chamfered_panel(
        draw,
        panel,
        border=(149, 156, 151),
        fill=(2, 7, 11, 242),
        cut=17,
        width=3,
    )

    entries = _bottom_stats(loadout)
    cell_width = (panel[2] - panel[0]) // len(entries)
    for index, (label, value, icon) in enumerate(entries):
        left = panel[0] + index * cell_width
        center_y = (panel[1] + panel[3]) // 2
        if index:
            draw.line(
                (left, panel[1] + 24, left, panel[3] - 24),
                fill=(138, 149, 147, 90),
                width=2,
            )
        _paste_stat_icon(canvas, icon, (left + 45, center_y), 52)
        label_font = _fit_font(label, cell_width - 88, 22)
        draw.text(
            (left + 82, panel[1] + 38),
            label,
            font=label_font,
            fill=(150, 161, 160),
            stroke_width=1,
            stroke_fill=(3, 7, 9),
        )
        draw.text(
            (left + 82, panel[1] + 73),
            value,
            font=_font(42, bold=True),
            fill=(232, 233, 225),
            stroke_width=1,
            stroke_fill=(3, 7, 9),
        )


def _draw_header(draw: ImageDraw.ImageDraw) -> None:
    title = "Э К И П И Р О В К А"
    draw.text(
        (800, 38),
        title,
        font=_font(47, display=True),
        anchor="mm",
        fill=(214, 216, 211),
        stroke_width=2,
        stroke_fill=(15, 18, 20),
    )
    draw.line((481, 39, 550, 39), fill=(157, 160, 153, 125), width=2)
    draw.line((1050, 39, 1119, 39), fill=(157, 160, 153, 125), width=2)


@lru_cache(maxsize=16)
def render_equipment_board(loadout: EquipmentLoadout) -> bytes:
    canvas = _background()
    _paste_character(canvas)
    draw = ImageDraw.Draw(canvas, "RGBA")
    _draw_header(draw)

    slots = {slot.slot_id: slot for slot in loadout.slots}
    left_top = 82
    left_height = 158
    left_gap = 4
    for index, slot_id in enumerate(_LEFT_SLOT_IDS):
        y1 = left_top + index * (left_height + left_gap)
        _draw_equipment_slot(
            canvas,
            draw,
            slots[slot_id],
            (48, y1, 181, y1 + 148),
            (194, y1 + 4, 390, y1 + 148),
        )

    right_top = 82
    right_step = 186
    for index, slot_id in enumerate(_RIGHT_SLOT_IDS):
        y1 = right_top + index * right_step
        _draw_equipment_slot(
            canvas,
            draw,
            slots[slot_id],
            (1210, y1, 1353, y1 + 163),
            (1367, y1 + 3, 1552, y1 + 163),
        )

    _draw_totals(canvas, draw, loadout)
    output = BytesIO()
    canvas.convert("RGB").save(
        output,
        format="JPEG",
        quality=92,
        optimize=True,
        progressive=True,
    )
    return output.getvalue()
