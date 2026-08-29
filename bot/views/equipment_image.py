from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from bot.models.equipment import EquipmentLoadout, EquipmentViewMode, EquippedSlot

_CANVAS_SIZE = (1600, 1900)
_CHARACTER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "character.png"
_FONT_DIRECTORY = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_REGULAR_FONT = _FONT_DIRECTORY / "DejaVuSans.ttf"
_BOLD_FONT = _FONT_DIRECTORY / "DejaVuSans-Bold.ttf"
_DISPLAY_FONT = _FONT_DIRECTORY / "DejaVuSerif-Bold.ttf"

_RARITY_COLORS = {
    "empty": (69, 79, 86, 210),
    "common": (181, 188, 190, 235),
    "uncommon": (66, 176, 106, 240),
    "rare": (55, 128, 221, 245),
    "epic": (143, 75, 226, 245),
}
_RARITY_TITLES = {
    "empty": "ПУСТО",
    "common": "ОБЫЧНОЕ",
    "uncommon": "НЕОБЫЧНОЕ",
    "rare": "РЕДКОЕ",
    "epic": "ЭПИЧЕСКОЕ",
}
_SLOT_GRID = (
    ("head", "shoulders", "amulet"),
    ("gloves", "body", "cloak"),
    ("ring_1", "belt", "ring_2"),
    ("earring_1", "pants", "earring_2"),
    ("main_hand", "boots", "off_hand"),
)


@lru_cache(maxsize=24)
def _font(
    size: int,
    *,
    bold: bool = False,
    display: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_path = _DISPLAY_FONT if display else (_BOLD_FONT if bold else _REGULAR_FONT)
    return ImageFont.truetype(font_path, size)


def enhancement_track(level: int, maximum: int = 10) -> tuple[bool, ...]:
    """Return a clamped sequence used to paint weapon-enhancement diamonds."""
    filled = max(0, min(level, maximum))
    return tuple(index < filled for index in range(maximum))


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


def _add_glow(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    blur: int = 30,
    width: int = 12,
) -> None:
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow, "RGBA")
    glow_draw.rounded_rectangle(box, radius=28, outline=(*color, 135), width=width)
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))


def _draw_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    accent: tuple[int, int, int],
    *,
    radius: int = 24,
    strong: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    fill = (7, 13, 18, 236) if strong else (8, 15, 20, 220)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=(*accent, 220), width=3)
    draw.rounded_rectangle(
        (x1 + 7, y1 + 7, x2 - 7, y2 - 7),
        radius=max(5, radius - 7),
        outline=(195, 211, 211, 36),
        width=1,
    )
    corner = 24
    ornament = (*accent, 175)
    draw.line(
        (x1 + 12, y1 + corner, x1 + 12, y1 + 12, x1 + corner, y1 + 12), fill=ornament, width=2
    )
    draw.line(
        (x2 - corner, y1 + 12, x2 - 12, y1 + 12, x2 - 12, y1 + corner), fill=ornament, width=2
    )
    draw.line(
        (x1 + 12, y2 - corner, x1 + 12, y2 - 12, x1 + corner, y2 - 12), fill=ornament, width=2
    )
    draw.line(
        (x2 - corner, y2 - 12, x2 - 12, y2 - 12, x2 - 12, y2 - corner), fill=ornament, width=2
    )


def _paint_atmosphere(source: Image.Image) -> Image.Image:
    background = ImageOps.fit(source, _CANVAS_SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(42))
    background = ImageEnhance.Brightness(background).enhance(0.13).convert("RGBA")

    tint = Image.new("RGBA", _CANVAS_SIZE, (0, 0, 0, 0))
    tint_draw = ImageDraw.Draw(tint, "RGBA")
    for y in range(_CANVAS_SIZE[1]):
        ratio = y / _CANVAS_SIZE[1]
        tint_draw.line((0, y, _CANVAS_SIZE[0], y), fill=(3, 10, 14, int(95 + 95 * ratio)))
    tint_draw.ellipse((-360, 20, 1050, 1200), fill=(34, 63, 69, 55))
    tint_draw.ellipse((830, 730, 1850, 1730), fill=(33, 25, 53, 50))
    background.alpha_composite(tint)

    fog = Image.new("RGBA", _CANVAS_SIZE, (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog, "RGBA")
    for ellipse in (
        (-280, 650, 900, 1160),
        (560, 820, 1760, 1270),
        (-350, 1450, 920, 1980),
        (680, 1460, 1850, 2030),
    ):
        fog_draw.ellipse(ellipse, fill=(133, 158, 161, 24))
    background.alpha_composite(fog.filter(ImageFilter.GaussianBlur(70)))
    return background


def _draw_rune_circle(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int) -> None:
    x, y = center
    color = (122, 157, 157, 42)
    for inset in (0, 18, 52):
        draw.ellipse(
            (x - radius + inset, y - radius + inset, x + radius - inset, y + radius - inset),
            outline=color,
            width=2,
        )
    for angle_point in ((0, -radius), (radius, 0), (0, radius), (-radius, 0)):
        px, py = x + angle_point[0], y + angle_point[1]
        draw.regular_polygon((px, py, 11), n_sides=4, rotation=45, outline=color)


def _paste_character(canvas: Image.Image, source: Image.Image) -> None:
    character = ImageOps.fit(
        source,
        (900, 790),
        method=Image.Resampling.LANCZOS,
        centering=(0.44, 0.28),
    )
    character = ImageEnhance.Contrast(character).enhance(1.16)
    character = ImageEnhance.Brightness(character).enhance(0.78).convert("RGBA")
    mask = Image.new("L", character.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle((0, 0, 900, 790), radius=40, fill=235)
    for y in range(630, 790):
        alpha = int(235 * (790 - y) / 160)
        mask_draw.line((0, y, 900, y), fill=alpha)
    canvas.paste(character, (42, 142), mask)


def _draw_slot_symbol(
    draw: ImageDraw.ImageDraw,
    slot_id: str,
    center: tuple[int, int],
    color: tuple[int, int, int],
    scale: int = 28,
) -> None:
    x, y = center
    line = (*color, 235)
    faint = (*color, 75)
    if slot_id == "head":
        draw.arc((x - scale, y - scale, x + scale, y + scale), 185, 355, fill=line, width=5)
        draw.line(
            (x - scale, y + 7, x - scale, y + 22, x, y + 31, x + scale, y + 22, x + scale, y + 7),
            fill=line,
            width=5,
        )
        draw.line((x, y - scale, x, y + 27), fill=faint, width=3)
    elif slot_id == "shoulders":
        draw.arc((x - 39, y - 16, x - 1, y + 28), 180, 345, fill=line, width=6)
        draw.arc((x + 1, y - 16, x + 39, y + 28), 195, 360, fill=line, width=6)
        draw.line((x - 25, y + 8, x, y + 25, x + 25, y + 8), fill=faint, width=3)
    elif slot_id == "body":
        draw.polygon(
            (
                (x - 30, y - 27),
                (x - 43, y + 8),
                (x - 20, y + 34),
                (x, y + 26),
                (x + 20, y + 34),
                (x + 43, y + 8),
                (x + 30, y - 27),
                (x, y - 12),
            ),
            outline=line,
        )
        draw.line((x, y - 12, x, y + 27), fill=faint, width=3)
    elif slot_id == "cloak":
        draw.polygon(
            (
                (x, y - 33),
                (x - 31, y - 12),
                (x - 20, y + 35),
                (x, y + 23),
                (x + 20, y + 35),
                (x + 31, y - 12),
            ),
            outline=line,
        )
        draw.arc((x - 12, y - 36, x + 12, y - 14), 0, 180, fill=line, width=4)
    elif slot_id == "belt":
        draw.line(
            (x - 42, y, x - 15, y, x - 15, y - 12, x + 15, y - 12, x + 15, y, x + 42, y),
            fill=line,
            width=6,
        )
        draw.rectangle((x - 12, y - 9, x + 12, y + 10), outline=faint, width=3)
    elif slot_id == "pants":
        draw.line((x - 25, y - 31, x + 25, y - 31, x + 17, y + 33), fill=line, width=6)
        draw.line((x - 25, y - 31, x - 17, y + 33), fill=line, width=6)
        draw.line((x, y - 16, x - 3, y + 30), fill=faint, width=3)
    elif slot_id == "boots":
        draw.line(
            (x - 28, y - 31, x - 23, y + 17, x - 40, y + 28, x - 3, y + 28), fill=line, width=6
        )
        draw.line(
            (x + 28, y - 31, x + 23, y + 17, x + 40, y + 28, x + 3, y + 28), fill=line, width=6
        )
    elif slot_id == "gloves":
        draw.rounded_rectangle((x - 24, y - 16, x + 24, y + 31), radius=10, outline=line, width=5)
        for offset in (-18, -6, 6, 18):
            draw.line((x + offset, y - 31, x + offset, y - 8), fill=line, width=4)
    elif slot_id.startswith("ring"):
        draw.ellipse((x - 25, y - 21, x + 25, y + 29), outline=line, width=6)
        draw.regular_polygon((x, y - 25, 13), n_sides=4, rotation=45, outline=faint)
    elif slot_id == "amulet":
        draw.arc((x - 34, y - 35, x + 34, y + 28), 15, 165, fill=line, width=4)
        draw.regular_polygon((x, y + 18, 20), n_sides=4, rotation=45, outline=line)
    elif slot_id.startswith("earring"):
        draw.arc((x - 19, y - 30, x + 19, y + 8), 190, 540, fill=line, width=5)
        draw.regular_polygon((x, y + 25, 16), n_sides=4, rotation=45, outline=faint)
    elif slot_id == "main_hand":
        draw.line((x - 7, y + 34, x + 5, y - 23), fill=line, width=7)
        draw.line((x - 18, y - 19, x + 18, y - 27), fill=line, width=6)
        draw.line((x + 5, y - 24, x + 4, y - 38), fill=faint, width=4)
    elif slot_id == "off_hand":
        draw.polygon(
            (
                (x, y - 35),
                (x + 35, y - 20),
                (x + 27, y + 17),
                (x, y + 36),
                (x - 27, y + 17),
                (x - 35, y - 20),
            ),
            outline=line,
        )
        draw.line((x, y - 25, x, y + 25), fill=faint, width=4)
        draw.line((x - 20, y, x + 20, y), fill=faint, width=4)


def _draw_slot_tile(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
    mode: EquipmentViewMode,
) -> None:
    x1, y1, x2, y2 = box
    accent = _RARITY_COLORS[slot.rarity][:3]
    if slot.occupied:
        _add_glow(canvas, box, accent, blur=18, width=7)
    _draw_panel(draw, box, accent, radius=18)
    draw.text(
        (x1 + 13, y1 + 10), slot.label.upper(), font=_font(15, bold=True), fill=(155, 168, 171)
    )
    _draw_slot_symbol(
        draw, slot.slot_id, ((x1 + x2) // 2, y1 + 64), accent if slot.occupied else (78, 88, 92), 23
    )

    if not slot.occupied:
        value = "ПУСТО"
        color = (86, 96, 100)
    elif mode is EquipmentViewMode.BONUSES:
        value = slot.bonuses[0] if slot.bonuses else "БЕЗ БОНУСОВ"
        color = accent
    else:
        value = slot.display_name
        color = (224, 229, 227)
    value_font = _font(16, bold=slot.occupied)
    value = _truncate(draw, value, value_font, x2 - x1 - 22)
    draw.text(((x1 + x2) // 2, y2 - 25), value, font=value_font, anchor="mm", fill=color)

    if slot.enhancement_level:
        badge = (x2 - 43, y1 + 9, x2 - 9, y1 + 39)
        draw.rounded_rectangle(
            badge, radius=9, fill=(*accent, 220), outline=(235, 242, 238, 130), width=1
        )
        draw.text(
            (x2 - 26, y1 + 24),
            f"+{slot.enhancement_level}",
            font=_font(13, bold=True),
            anchor="mm",
            fill=(245, 248, 244),
        )


def _draw_diamond_track(
    draw: ImageDraw.ImageDraw,
    origin: tuple[int, int],
    level: int,
    accent: tuple[int, int, int],
    *,
    size: int = 17,
    gap: int = 12,
) -> None:
    x, y = origin
    for index, filled in enumerate(enhancement_track(level)):
        center_x = x + index * (size * 2 + gap)
        points = (
            (center_x, y - size),
            (center_x + size, y),
            (center_x, y + size),
            (center_x - size, y),
        )
        if filled:
            draw.polygon(points, fill=(*accent, 235), outline=(225, 239, 235, 220))
            inner = size // 2
            draw.polygon(
                (
                    (center_x, y - inner),
                    (center_x + inner, y),
                    (center_x, y + inner),
                    (center_x - inner, y),
                ),
                fill=(226, 247, 243, 105),
            )
        else:
            draw.polygon(points, fill=(8, 14, 18, 225), outline=(116, 128, 129, 155))


def _paste_staff_focus(
    canvas: Image.Image, source: Image.Image, box: tuple[int, int, int, int]
) -> None:
    x1, y1, x2, y2 = box
    staff_crop = source.crop((135, 0, 420, 1250))
    staff = ImageOps.fit(
        staff_crop, (x2 - x1, y2 - y1), method=Image.Resampling.LANCZOS, centering=(0.48, 0.38)
    )
    staff = ImageEnhance.Contrast(staff).enhance(1.24)
    staff = ImageEnhance.Brightness(staff).enhance(0.72).convert("RGBA")
    mask = Image.new("L", staff.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *staff.size), radius=24, fill=225)
    canvas.paste(staff, (x1, y1), mask)


def _draw_bonus_rows(
    draw: ImageDraw.ImageDraw,
    bonuses: tuple[str, ...],
    origin: tuple[int, int],
    color: tuple[int, int, int],
    *,
    maximum: int = 4,
    line_height: int = 39,
) -> None:
    x, y = origin
    for index, bonus in enumerate(bonuses[:maximum]):
        row_y = y + index * line_height
        draw.regular_polygon((x + 9, row_y + 12, 5), n_sides=4, rotation=45, fill=(*color, 210))
        draw.text((x + 28, row_y), bonus, font=_font(24), fill=(205, 217, 214))


def _draw_main_weapon_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    source: Image.Image,
    slot: EquippedSlot,
) -> None:
    box = (40, 1010, 1020, 1585)
    accent = _RARITY_COLORS[slot.rarity][:3]
    _add_glow(canvas, box, accent, blur=34, width=13)
    _draw_panel(draw, box, accent, radius=30, strong=True)
    draw.text((78, 1044), "ОСНОВНАЯ РУКА", font=_font(21, bold=True), fill=(139, 157, 157))
    draw.text(
        (78, 1080), slot.display_name.upper(), font=_font(43, display=True), fill=(237, 239, 231)
    )
    draw.text((78, 1142), _RARITY_TITLES[slot.rarity], font=_font(18, bold=True), fill=accent)

    _paste_staff_focus(canvas, source, (76, 1190, 362, 1530))
    draw.rounded_rectangle((75, 1189, 363, 1531), radius=25, outline=(*accent, 150), width=2)
    draw.text((402, 1190), "РЕЗОНАНС ОРУЖИЯ", font=_font(19, bold=True), fill=(137, 153, 153))
    _draw_bonus_rows(draw, slot.bonuses, (402, 1236), accent, maximum=3, line_height=42)
    draw.text(
        (402, 1382),
        f"ЗАТОЧКА  +{slot.enhancement_level}",
        font=_font(27, bold=True),
        fill=(232, 237, 229),
    )
    _draw_diamond_track(draw, (420, 1450), slot.enhancement_level, accent, size=18, gap=13)
    draw.text((402, 1492), "10 ступеней усиления", font=_font(18), fill=(119, 134, 135))


def _draw_offhand_card(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
) -> None:
    box = (1045, 1010, 1560, 1585)
    accent = _RARITY_COLORS[slot.rarity][:3]
    _add_glow(canvas, box, accent, blur=27, width=10)
    _draw_panel(draw, box, accent, radius=30, strong=True)
    draw.text((1080, 1044), "ВТОРАЯ РУКА", font=_font(21, bold=True), fill=(139, 157, 157))
    name = _truncate(draw, slot.display_name.upper(), _font(31, display=True), 438)
    draw.text((1080, 1080), name, font=_font(31, display=True), fill=(237, 239, 231))
    draw.text((1080, 1128), _RARITY_TITLES[slot.rarity], font=_font(18, bold=True), fill=accent)

    _draw_slot_symbol(draw, slot.slot_id, (1302, 1242), accent, 58)
    draw.ellipse((1221, 1160, 1383, 1322), outline=(*accent, 70), width=2)
    _draw_bonus_rows(draw, slot.bonuses, (1090, 1340), accent, maximum=3, line_height=38)
    draw.text(
        (1090, 1470),
        f"ЗАТОЧКА  +{slot.enhancement_level}",
        font=_font(22, bold=True),
        fill=(220, 227, 220),
    )
    _draw_diamond_track(draw, (1107, 1530), slot.enhancement_level, accent, size=11, gap=9)


def _stat_value(loadout: EquipmentLoadout, marker: str, fallback: str) -> str:
    for bonus in loadout.total_bonuses:
        if marker in bonus:
            return bonus.split(marker, maxsplit=1)[1].strip()
    return fallback


def _draw_summary(draw: ImageDraw.ImageDraw, loadout: EquipmentLoadout) -> None:
    box = (40, 1625, 1560, 1845)
    _draw_panel(draw, box, (107, 129, 128), radius=26)
    draw.text((80, 1654), "СИЛА СНАРЯЖЕНИЯ", font=_font(23, display=True), fill=(178, 190, 183))
    metrics = (
        ("HP", _stat_value(loadout, "HP", "750")),
        ("ЗАЩИТА", _stat_value(loadout, "Защита", "61")),
        ("МАГ. ЗАЩ", _stat_value(loadout, "Маг. защита", "58")),
        ("МАГ. АТАКА", _stat_value(loadout, "Маг. атака", "67")),
        ("СКОРОСТЬ", _stat_value(loadout, "Скорость", "+15%")),
    )
    for index, (label, value) in enumerate(metrics):
        x = 82 + index * 296
        if index:
            draw.line((x - 30, 1706, x - 30, 1815), fill=(122, 139, 138, 50), width=2)
        draw.text((x, 1713), label, font=_font(17, bold=True), fill=(120, 138, 138))
        draw.text((x, 1750), value, font=_font(40, display=True), fill=(224, 232, 224))


@lru_cache(maxsize=8)
def render_equipment_board(
    loadout: EquipmentLoadout,
    mode: EquipmentViewMode = EquipmentViewMode.ITEMS,
) -> bytes:
    source = Image.open(_CHARACTER_IMAGE).convert("RGB")
    canvas = _paint_atmosphere(source)
    draw = ImageDraw.Draw(canvas, "RGBA")

    draw.rectangle((0, 0, 1600, 126), fill=(3, 8, 11, 225))
    draw.line((70, 111, 1530, 111), fill=(116, 141, 139, 70), width=2)
    draw.regular_polygon((800, 111, 8), n_sides=4, rotation=45, fill=(143, 166, 160, 110))
    draw.text(
        (800, 24), "СНАРЯЖЕНИЕ", font=_font(47, display=True), anchor="ma", fill=(229, 233, 224)
    )
    subtitle = (
        f"{loadout.character_name.upper()}  ·  {loadout.occupied_count}/{len(loadout.slots)} СЛОТОВ"
    )
    draw.text(
        (800, 83),
        subtitle,
        font=_font(19, bold=True),
        anchor="ma",
        fill=(135, 151, 151),
    )

    _draw_rune_circle(draw, (472, 520), 330)
    _paste_character(canvas, source)
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rounded_rectangle((38, 138, 948, 942), radius=42, outline=(125, 150, 147, 92), width=3)
    draw.text((78, 880), "АКОЛИТ ТУМАНА", font=_font(21, display=True), fill=(181, 194, 187))
    draw.text((78, 909), "Сила скрыта в снаряжении", font=_font(17), fill=(115, 131, 131))

    slots_by_id = {slot.slot_id: slot for slot in loadout.slots}
    for row, slot_ids in enumerate(_SLOT_GRID):
        for column, slot_id in enumerate(slot_ids):
            x = 980 + column * 194
            y = 150 + row * 158
            _draw_slot_tile(canvas, draw, slots_by_id[slot_id], (x, y, x + 174, y + 138), mode)

    main_hand = slots_by_id["main_hand"]
    off_hand = slots_by_id["off_hand"]
    _draw_main_weapon_card(canvas, draw, source, main_hand)
    _draw_offhand_card(canvas, draw, off_hand)
    _draw_summary(draw, loadout)

    draw.text(
        (800, 1872),
        "FOG · EQUIPMENT MATRIX",
        font=_font(14, bold=True),
        anchor="mm",
        fill=(86, 103, 103),
    )
    output = BytesIO()
    canvas.convert("RGB").save(output, format="JPEG", quality=90, optimize=True)
    return output.getvalue()
