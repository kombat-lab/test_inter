from __future__ import annotations

from dataclasses import replace

from bot.services.characters import get_character
from bot.views.character import render_character_caption


def test_character_caption_contains_reference_data() -> None:
    caption = render_character_caption(get_character())

    assert "🧙 <b>Kombat</b>" in caption
    assert "<b>Kombat</b>" in caption
    assert "<b>Уровень 18</b>  ·  89%" in caption
    assert "\u2060".join(["🟩"] * 9 + ["⬛️"]) in caption
    assert "212 435 / 238 650 XP" in caption
    assert "✨ Пыль: <b>70 258</b>\n💎 Кристаллы: <b>213</b>" in caption
    assert "🔮 Благословение тумана · 17д 8ч" in caption
    assert "💍 Серьга дропа (30 дней) ×2 · 29д 23ч" in caption
    assert "28м" not in caption
    assert "46с" not in caption
    assert len(caption) <= 1024


def test_progress_color_changes_with_completion() -> None:
    character = get_character()
    orange = render_character_caption(
        replace(character, experience=30, experience_to_next_level=100)
    )
    yellow = render_character_caption(
        replace(character, experience=60, experience_to_next_level=100)
    )
    green = render_character_caption(
        replace(character, experience=70, experience_to_next_level=100)
    )

    assert "\u2060".join(["🟧"] * 3 + ["⬛️"] * 7) in orange
    assert "\u2060".join(["🟨"] * 6 + ["⬛️"] * 4) in yellow
    assert "\u2060".join(["🟩"] * 7 + ["⬛️"] * 3) in green


def test_expanded_character_caption_contains_all_buffs() -> None:
    caption = render_character_caption(get_character(), expanded_buffs=True)

    assert caption.count("Серьга дропа (30 дней)") == 1
    assert "<b>💍 Серьга дропа (30 дней) ×2</b> · 29д 23ч" in caption
    assert "└ Лут +30% · Пыль +30% · XP +30%" in caption
    assert len(caption) <= 1024


def test_character_caption_escapes_dynamic_values() -> None:
    character = get_character()
    unsafe_character = replace(character, name="<Kombat>")

    assert "&lt;Kombat&gt;" in render_character_caption(unsafe_character)
