from __future__ import annotations

from html import escape

from bot.models.character import ActiveBuff, Character


def _render_buff(buff: ActiveBuff) -> list[str]:
    name = escape(buff.name)
    remaining = escape(buff.remaining)
    effects = tuple(escape(effect) for effect in buff.effects)

    if buff.inline and len(effects) == 1:
        return [f"• {name}: {effects[0]} — {remaining}"]

    return [
        f"• {name} — {remaining}:",
        *(f"  {effect}" for effect in effects),
    ]


def render_character_caption(character: Character) -> str:
    lines = [
        "📍 <b>Персонаж</b>",
        "",
        f"🪬 🧍 <b>{escape(character.name)}</b>",
        f"• Уровень: {character.level}",
        f"• Опыт: {character.experience} / {character.experience_to_next_level}",
        f"• Туманная пыль: ✨ {character.mist_dust} ед.",
        f"• Туманные кристаллы: 💎 {character.mist_crystals}",
        f"• Боевой класс: {escape(character.combat_class)}",
        f"• Путь: {escape(character.path)}",
        "",
        "<b>Активные бафы:</b>",
    ]
    for buff in character.active_buffs:
        lines.extend(_render_buff(buff))
    return "\n".join(lines)
