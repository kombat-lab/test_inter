from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

from bot.models.equipment import EquipmentLoadout, EquippedSlot

_CANVAS_SIZE = (1600, 1600)
_ASSET_DIRECTORY = Path(__file__).resolve().parents[1] / "assets"
_EQUIPMENT_ASSET_DIRECTORY = _ASSET_DIRECTORY / "equipment"
_CHARACTER_IMAGE = _ASSET_DIRECTORY / "character.png"
_FONT_DIRECTORY = _ASSET_DIRECTORY / "fonts"
_REGULAR_FONT = _FONT_DIRECTORY / "DejaVuSans.ttf"
_BOLD_FONT = _FONT_DIRECTORY / "DejaVuSans-Bold.ttf"
_DISPLAY_FONT = _FONT_DIRECTORY / "DejaVuSerif-Bold.ttf"

_RARITY_COLORS = {
    "empty": (78, 87, 94),
    "common": (202, 207, 205),
    "uncommon": (62, 199, 88),
    "rare": (52, 137, 234),
    "epic": (166, 73, 232),
}
_CARD_COLORS = {
    "common": (184, 190, 188),
    "uncommon": (61, 187, 91),
    "rare": (54, 134, 224),
    "epic": (159, 73, 220),
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


@lru_cache(maxsize=32)
def _font(
    size: int,
    *,
    bold: bool = False,
    display: bool = False,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = _DISPLAY_FONT if display else (_BOLD_FONT if bold else _REGULAR_FONT)
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=24)
def _source_image(path: str) -> Image.Image:
    with Image.open(path) as source:
        return source.convert("RGB")


def _rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    outline: tuple[int, int, int],
    fill: tuple[int, int, int, int] = (7, 13, 18, 232),
    radius: int = 18,
    width: int = 3,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=(*outline, 225), width=width)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(
        (x1 + 6, y1 + 6, x2 - 6, y2 - 6),
        radius=max(4, radius - 6),
        outline=(222, 232, 229, 30),
        width=1,
    )


def _add_glow(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer, "RGBA")
    layer_draw.rounded_rectangle(box, radius=20, outline=(*color, 115), width=8)
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(20)))


def _background(character: Image.Image) -> Image.Image:
    background = ImageOps.fit(character, _CANVAS_SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(45))
    background = ImageEnhance.Brightness(background).enhance(0.22).convert("RGBA")

    tint = Image.new("RGBA", _CANVAS_SIZE, (0, 0, 0, 0))
    tint_draw = ImageDraw.Draw(tint, "RGBA")
    for y in range(_CANVAS_SIZE[1]):
        ratio = y / _CANVAS_SIZE[1]
        tint_draw.line((0, y, 1600, y), fill=(3, 8, 12, int(90 + ratio * 90)))
    tint_draw.rectangle((0, 0, 410, 1390), fill=(2, 7, 10, 145))
    tint_draw.rectangle((1190, 0, 1600, 1390), fill=(2, 7, 10, 145))
    background.alpha_composite(tint)
    return background


def _paste_character(canvas: Image.Image, character: Image.Image) -> None:
    target = (388, 92, 1212, 1372)
    width = target[2] - target[0]
    height = target[3] - target[1]
    fitted = ImageOps.fit(
        character,
        (width, height),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    ).convert("RGBA")
    fitted = ImageEnhance.Contrast(fitted).enhance(1.04)

    mask = Image.new("L", fitted.size, 255)
    mask_draw = ImageDraw.Draw(mask)
    for inset in range(54):
        alpha = int(255 * inset / 54)
        mask_draw.rectangle((inset, 0, inset + 1, height), fill=alpha)
        mask_draw.rectangle((width - inset - 2, 0, width - inset - 1, height), fill=alpha)
    for y in range(1180, height):
        alpha = int(255 * (height - y) / max(1, height - 1180))
        mask_draw.line((0, y, width, y), fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    canvas.paste(fitted, (target[0], target[1]), mask)


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
    if key == "intelligence":
        color = (232, 220, 196, 255)
        for dx, dy in ((-5, -4), (4, -5), (-5, 4), (5, 4)):
            draw.ellipse((x + dx - 6, y + dy - 6, x + dx + 6, y + dy + 6), fill=color)
        draw.line((x, y - 11, x, y + 11), fill=(94, 82, 77, 180), width=2)
    elif key == "regeneration":
        color = (239, 223, 207, 255)
        draw.ellipse((x - 11, y - 9, x, y + 3), fill=color)
        draw.ellipse((x, y - 9, x + 11, y + 3), fill=color)
        draw.polygon(((x - 11, y - 3), (x + 11, y - 3), (x, y + 13)), fill=color)
    elif key == "luck":
        color = (122, 203, 75, 255)
        for dx, dy in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
            draw.ellipse((x + dx - 6, y + dy - 6, x + dx + 6, y + dy + 6), fill=color)
        draw.line((x + 2, y + 6, x + 8, y + 15), fill=color, width=3)
    elif key == "defense":
        color = (206, 218, 211, 255)
        draw.polygon(
            (
                (x, y - size),
                (x + size, y - 6),
                (x + 8, y + 8),
                (x, y + size),
                (x - 8, y + 8),
                (x - size, y - 6),
            ),
            fill=color,
        )
        draw.line((x, y - 8, x, y + 8), fill=(61, 93, 111, 210), width=3)
    elif key == "magic_defense":
        color = (220, 220, 187, 255)
        draw.ellipse((x - size, y - size, x + size, y + size), outline=color, width=3)
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(65, 144, 216, 255))
        draw.line((x, y - size - 3, x, y - size - 9), fill=color, width=3)
    elif key == "critical_power":
        draw.polygon(_star_points(center, size + 2, 5, 8), fill=(238, 155, 62, 255))
    elif key == "critical":
        draw.polygon(_star_points(center, size + 1, 7, 4), fill=(224, 59, 54, 255))
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(31, 16, 18, 255))
    elif key == "drop":
        color = (232, 220, 190, 255)
        draw.rounded_rectangle((x - size, y - size, x + size, y + size), radius=4, fill=color)
        for dx, dy in ((-6, -6), (6, 6), (-6, 6), (6, -6), (0, 0)):
            draw.ellipse(
                (x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2),
                fill=(65, 52, 44, 255),
            )
    elif key == "speed":
        color = (229, 221, 192, 255)
        draw.ellipse((x - 8, y + 1, x + 8, y + 13), fill=color)
        for dx, dy in ((-10, -7), (-3, -11), (5, -10), (11, -5)):
            draw.ellipse((x + dx - 4, y + dy - 4, x + dx + 4, y + dy + 4), fill=color)
    elif key == "block":
        color = (182, 119, 70, 255)
        draw.rectangle((x - size, y - 9, x + size, y + 10), fill=color)
        draw.line((x - size, y, x + size, y), fill=(63, 40, 29, 220), width=2)
        draw.line((x, y - 9, x, y), fill=(63, 40, 29, 220), width=2)
        draw.line((x - 6, y, x - 6, y + 10), fill=(63, 40, 29, 220), width=2)
        draw.line((x + 7, y, x + 7, y + 10), fill=(63, 40, 29, 220), width=2)
    elif key == "hp":
        _draw_stat_icon(draw, "regeneration", center, size)
        draw.line((x - 6, y + 1, x + 6, y + 1), fill=(218, 47, 51, 255), width=3)
        draw.line((x, y - 5, x, y + 7), fill=(218, 47, 51, 255), width=3)
    elif key == "attack":
        color = (207, 213, 211, 255)
        draw.line((x - 8, y + 10, x + 8, y - 10), fill=color, width=5)
        draw.line((x - 10, y - 1, x + 1, y + 10), fill=color, width=3)
    elif key == "magic_attack":
        draw.ellipse(
            (x - size, y - size, x + size, y + size),
            fill=(91, 60, 157, 255),
            outline=(219, 207, 245, 255),
            width=2,
        )
        draw.ellipse((x - 4, y - 6, x + 3, y + 1), fill=(220, 230, 255, 220))


def _draw_lock(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    x, y = origin
    draw.arc((x - 9, y - 10, x + 9, y + 9), 180, 360, fill=(244, 203, 91, 255), width=4)
    draw.rounded_rectangle((x - 11, y, x + 11, y + 18), radius=4, fill=(239, 190, 65, 255))
    draw.ellipse((x - 2, y + 6, x + 2, y + 10), fill=(63, 46, 28, 255))


def _draw_card_socket(
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    if slot.card is None:
        draw.rounded_rectangle(
            box,
            radius=4,
            fill=(5, 10, 14, 230),
            outline=(112, 125, 126, 205),
            width=2,
        )
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        draw.polygon(
            (
                (center_x, center_y - 5),
                (center_x + 5, center_y),
                (center_x, center_y + 5),
                (center_x - 5, center_y),
            ),
            outline=(102, 117, 117, 185),
        )
        draw.line((x2 - 7, y1 + 1, x2 - 1, y1 + 7), fill=(112, 125, 126, 165), width=1)
        return
    color = _CARD_COLORS.get(slot.card.rarity, _CARD_COLORS["common"])
    draw.rounded_rectangle(
        box,
        radius=4,
        fill=(*color, 210),
        outline=(235, 242, 236, 220),
        width=2,
    )
    draw.regular_polygon(
        ((x1 + x2) // 2, (y1 + y2) // 2, 7),
        n_sides=4,
        rotation=45,
        fill=(226, 239, 235, 215),
    )


def _item_art(slot: EquippedSlot) -> Image.Image | None:
    if not slot.asset_name:
        return None
    path = _EQUIPMENT_ASSET_DIRECTORY / slot.asset_name
    if not path.exists():
        return None
    return _source_image(str(path))


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
        centering=(0.5, 0.45),
    )
    art = ImageEnhance.Contrast(art).enhance(1.08).convert("RGBA")
    mask = Image.new("L", art.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *art.size), radius=12, fill=238)
    canvas.paste(art, (x1, y1), mask)


def _draw_empty_symbol(
    draw: ImageDraw.ImageDraw,
    slot_id: str,
    center: tuple[int, int],
) -> None:
    x, y = center
    color = (87, 98, 104, 230)
    if slot_id.startswith("ring"):
        draw.ellipse((x - 31, y - 27, x + 31, y + 35), outline=color, width=6)
        draw.regular_polygon((x, y - 31, 14), n_sides=4, rotation=45, outline=color)
    else:
        draw.arc((x - 42, y - 45, x + 42, y + 36), 15, 165, fill=color, width=5)
        draw.regular_polygon((x, y + 24, 24), n_sides=4, rotation=45, outline=color)


def _bonus_parts(bonus: str) -> tuple[str, str]:
    for prefix, key in _BONUS_PREFIXES:
        if bonus.startswith(prefix):
            return key, bonus[len(prefix) :].strip()
    return "", bonus


def _draw_bonus_grid(
    draw: ImageDraw.ImageDraw,
    bonuses: tuple[str, ...],
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    if not bonuses:
        draw.text(
            ((x1 + x2) // 2, (y1 + y2) // 2),
            "—",
            font=_font(27, bold=True),
            anchor="mm",
            fill=(104, 116, 118),
        )
        return
    columns = 2
    rows = (len(bonuses) + columns - 1) // columns
    row_height = min(29, max(23, (y2 - y1) // max(rows, 1)))
    column_width = (x2 - x1) // columns
    for index, bonus in enumerate(bonuses):
        column = index % columns
        row = index // columns
        key, value = _bonus_parts(bonus)
        center_x = x1 + column * column_width + 15
        center_y = y1 + row * row_height + row_height // 2
        if key:
            _draw_stat_icon(draw, key, (center_x, center_y), 10)
        draw.text(
            (center_x + 19, center_y),
            value,
            font=_font(22, bold=True),
            anchor="lm",
            fill=(118, 222, 116),
        )


def _draw_equipment_row(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    slot: EquippedSlot,
    box: tuple[int, int, int, int],
) -> None:
    x1, y1, x2, y2 = box
    accent = _RARITY_COLORS.get(slot.rarity, _RARITY_COLORS["empty"])
    if slot.occupied:
        _add_glow(canvas, (x1, y1, x1 + 132, y2), accent)
    _rounded_panel(draw, box, outline=(74, 86, 91), radius=16)
    icon_box = (x1, y1, x1 + 132, y2)
    draw.rounded_rectangle(
        icon_box,
        radius=16,
        fill=(6, 11, 15, 238),
        outline=(*accent, 245),
        width=4,
    )
    draw.line((x1 + 141, y1 + 11, x1 + 141, y2 - 11), fill=(126, 143, 143, 55), width=2)

    if slot.occupied:
        _paste_item_art(canvas, slot, (x1 + 8, y1 + 8, x1 + 124, y2 - 8))
        _draw_lock(draw, (x1 + 111, y1 + 16))
        _draw_card_socket(draw, slot, (x1 + 94, y2 - 39, x1 + 119, y2 - 9))
        if slot.enhancement_level:
            draw.text(
                (x1 + 13, y1 + 8),
                f"+{slot.enhancement_level}",
                font=_font(25, bold=True),
                fill=(226, 231, 244),
                stroke_width=2,
                stroke_fill=(7, 10, 15),
            )
    else:
        _draw_empty_symbol(draw, slot.slot_id, (x1 + 66, (y1 + y2) // 2))

    plate = (x1 + 151, y1 + 8, x2 - 8, y2 - 8)
    draw.text(
        (plate[0], plate[1]),
        slot.label.upper(),
        font=_font(15, bold=True),
        fill=(135, 149, 151),
    )
    if not slot.occupied:
        draw.text(
            ((plate[0] + plate[2]) // 2, (plate[1] + plate[3]) // 2 + 9),
            "ПУСТО",
            font=_font(25, bold=True),
            anchor="mm",
            fill=(107, 118, 121),
        )
        return
    _draw_bonus_grid(draw, slot.bonuses, (plate[0], plate[1] + 28, plate[2], plate[3]))


def _clean_total(text: str) -> str:
    value = text.strip()
    while value and not value[0].isalnum():
        value = value[1:].lstrip()
    return value


def _total_value(loadout: EquipmentLoadout, marker: str, fallback: str = "0") -> str:
    for item in loadout.total_bonuses:
        clean = _clean_total(item)
        if clean.startswith(marker):
            return clean[len(marker) :].strip()
    return fallback


def _draw_footer(draw: ImageDraw.ImageDraw, loadout: EquipmentLoadout) -> None:
    _rounded_panel(
        draw,
        (30, 1390, 1570, 1570),
        outline=(95, 113, 116),
        radius=20,
        fill=(4, 9, 13, 245),
        width=3,
    )
    metrics = (
        ("hp", "HP", _total_value(loadout, "HP", "750")),
        ("speed", "СКОРОСТЬ", _total_value(loadout, "Скорость", "+15%")),
        ("defense", "ЗАЩИТА", _total_value(loadout, "Защита", "61")),
        ("magic_defense", "МАГ. ЗАЩИТА", _total_value(loadout, "Маг. защита", "58")),
        ("critical", "КРИТ", _total_value(loadout, "Крит", "3")),
        ("attack", "АТАКА", _total_value(loadout, "Атака", "1")),
        ("magic_attack", "МАГ. АТАКА", _total_value(loadout, "Маг. атака", "67")),
        ("block", "БЛОК", _total_value(loadout, "Блок", "8")),
        ("hp", "ЭКИП. HP", _total_value(loadout, "Бонус HP от экипа", "+0")),
        (
            "speed",
            "ЭКИП. СКОРОСТЬ",
            _total_value(loadout, "Бонус скорости от экипа", "+15%"),
        ),
    )
    cell_width = 304
    for index, (icon, label, value) in enumerate(metrics):
        row = index // 5
        column = index % 5
        x = 55 + column * cell_width
        y = 1412 + row * 78
        if column:
            draw.line((x - 17, y + 2, x - 17, y + 58), fill=(121, 137, 139, 55), width=2)
        _draw_stat_icon(draw, icon, (x + 17, y + 30), 13)
        draw.text((x + 42, y + 8), label, font=_font(17, bold=True), fill=(152, 166, 166))
        draw.text((x + 42, y + 32), value, font=_font(29, bold=True), fill=(228, 233, 226))


def _draw_header(draw: ImageDraw.ImageDraw, loadout: EquipmentLoadout) -> None:
    draw.rectangle((0, 0, 1600, 88), fill=(3, 8, 11, 244))
    draw.line((35, 82, 1565, 82), fill=(135, 151, 151, 75), width=2)
    draw.text(
        (800, 11),
        "ЭКИПИРОВКА",
        font=_font(48, display=True),
        anchor="ma",
        fill=(226, 231, 224),
    )
    draw.text(
        (38, 28),
        f"{loadout.occupied_count}/15",
        font=_font(22, bold=True),
        fill=(133, 149, 151),
    )
    card_x = 1324
    draw.rounded_rectangle(
        (card_x, 23, card_x + 23, 55),
        radius=4,
        outline=(163, 177, 176, 210),
        width=2,
    )
    draw.polygon(
        (
            (card_x + 12, 32),
            (card_x + 18, 39),
            (card_x + 12, 46),
            (card_x + 6, 39),
        ),
        outline=(135, 155, 153, 190),
    )
    draw.text(
        (card_x + 34, 38),
        "1 КАРТА НА ПРЕДМЕТ",
        font=_font(16, bold=True),
        anchor="lm",
        fill=(135, 151, 151),
    )


@lru_cache(maxsize=16)
def render_equipment_board(loadout: EquipmentLoadout) -> bytes:
    character = _source_image(str(_CHARACTER_IMAGE))
    canvas = _background(character)
    _paste_character(canvas, character)
    draw = ImageDraw.Draw(canvas, "RGBA")
    _draw_header(draw, loadout)

    slots = {slot.slot_id: slot for slot in loadout.slots}
    left_top = 105
    left_height = 151
    left_gap = 8
    for index, slot_id in enumerate(_LEFT_SLOT_IDS):
        y1 = left_top + index * (left_height + left_gap)
        _draw_equipment_row(canvas, draw, slots[slot_id], (28, y1, 388, y1 + left_height))

    right_top = 105
    right_height = 166
    right_gap = 15
    for index, slot_id in enumerate(_RIGHT_SLOT_IDS):
        y1 = right_top + index * (right_height + right_gap)
        _draw_equipment_row(canvas, draw, slots[slot_id], (1212, y1, 1572, y1 + right_height))

    draw.rounded_rectangle(
        (394, 96, 1206, 1377),
        radius=26,
        outline=(123, 142, 143, 68),
        width=3,
    )
    _draw_footer(draw, loadout)

    output = BytesIO()
    canvas.convert("RGB").save(
        output,
        format="JPEG",
        quality=91,
        optimize=True,
        progressive=True,
    )
    return output.getvalue()
