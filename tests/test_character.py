from __future__ import annotations

from bot.services.characters import get_character
from bot.views.character import render_character_caption


def test_character_caption_contains_reference_data() -> None:
    caption = render_character_caption(get_character())

    assert "📍 <b>Персонаж</b>" in caption
    assert "<b>Kombat</b>" in caption
    assert "• Уровень: 18" in caption
    assert "• Опыт: 212435 / 238650" in caption
    assert "✨ 70258 ед." in caption
    assert "💎 213" in caption
    assert caption.count("Серьга дропа (30 дней)") == 2
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
