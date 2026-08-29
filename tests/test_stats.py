from __future__ import annotations

from bot.keyboards.stats import stats_keyboard
from bot.services.stats import get_character_stats
from bot.views.stats import render_stats_caption


def test_compact_stats_caption_contains_core_values() -> None:
    caption = render_stats_caption(get_character_stats())

    assert "📊 <b>Характеристики</b>" in caption
    assert "❤️ <b>750 / 750 HP</b>" in caption
    assert "🔮 Маг. урон <b>74–80</b>" in caption
    assert "🧙 Аколит" not in caption
    assert "🧠 <b>56</b> · ❤️‍🩹 <b>38</b>" in caption
    assert "🛡 <b>61</b> · 🪬 <b>58</b> · 🧱 <b>10.6%</b>" in caption
    assert "💢 Крит <b>3</b>" in caption
    assert "🍀 Ид. крит <b>1</b>" in caption
    assert "🌪 Ид. уворот <b>1</b>" in caption
    assert "⚡ Инициатива <b>50</b>" in caption
    assert "🐾 Скорость <b>+15.0%</b>" in caption
    assert "🔘 Свободные очки: <b>0</b>" in caption
    assert len(caption) <= 1024


def test_expanded_stats_caption_contains_secondary_values() -> None:
    caption = render_stats_caption(get_character_stats(), expanded=True)

    assert "<b>Дополнительные боевые показатели</b>" in caption
    assert "🔮 Маг. атака <b>67</b>" in caption
    assert "Сила крита <b>5.0%</b>" in caption
    assert caption.count("Ид. уворот") == 1
    assert len(caption) <= 1024


def test_stats_keyboard_expands_and_collapses() -> None:
    compact = stats_keyboard()
    expanded = stats_keyboard(expanded=True)

    assert compact.inline_keyboard[0][0].text == "📋 Все показатели"
    assert compact.inline_keyboard[0][0].callback_data == "character:stats_details"
    assert expanded.inline_keyboard[0][0].text == "📊 Свернуть"
    assert expanded.inline_keyboard[0][0].callback_data == "character:stats"
    assert compact.inline_keyboard[-1][0].callback_data == "character:overview"
