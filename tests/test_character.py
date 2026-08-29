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
    assert "✨ <b>70 258</b> пыли" in caption
    assert "💎 <b>213</b> кристаллов" in caption
    assert "Ещё эффектов: 2" in caption
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

    assert caption.count("Серьга дропа (30 дней)") == 2
    assert "Ещё эффектов" not in caption
    assert len(caption) <= 1024


def test_character_caption_escapes_dynamic_values() -> None:
    character = get_character()
    unsafe_character = type(character)(
        name="<Kombat>",
        level=character.level,
        experience=character.experience,
        experience_to_next_level=character.experience_to_next_level,
        mist_dust=character.mist_dust,
        mist_crystals=character.mist_crystals,
        combat_class=character.combat_class,
        path=character.path,
        active_buffs=character.active_buffs,
    )

    assert "&lt;Kombat&gt;" in render_character_caption(unsafe_character)
