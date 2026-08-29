from __future__ import annotations

from html import escape

from bot.models.character import ActiveBuff, Character

_PROGRESS_SEGMENTS = 10


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _render_progress(character: Character) -> tuple[str, int]:
    if character.experience_to_next_level <= 0:
        return "░" * _PROGRESS_SEGMENTS, 0

    ratio = min(character.experience / character.experience_to_next_level, 1.0)
    percentage = round(ratio * 100)
    filled = round(ratio * _PROGRESS_SEGMENTS)
    bar = "█" * filled + "░" * (_PROGRESS_SEGMENTS - filled)
    return bar, percentage


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


def render_character_caption(
    character: Character,
    *,
    expanded_buffs: bool = False,
) -> str:
    progress, percentage = _render_progress(character)
    lines = [
        f"🧙 <b>{escape(character.name)}</b>",
        f"<i>{escape(character.combat_class)} · Путь {escape(character.path)}</i>",
        "",
        f"<b>Уровень {character.level}</b>  ·  {percentage}%",
        f"<code>{progress}</code>",
        f"{_format_number(character.experience)} / "
        f"{_format_number(character.experience_to_next_level)} XP",
        "",
        f"✨ <b>{_format_number(character.mist_dust)}</b> пыли   "
        f"💎 <b>{_format_number(character.mist_crystals)}</b> кристаллов",
        "",
        f"🌫 <b>Активные эффекты · {len(character.active_buffs)}</b>",
    ]
    if expanded_buffs:
        for buff in character.active_buffs:
            lines.extend(_render_buff(buff))
    elif character.active_buffs:
        first_buff = character.active_buffs[0]
        lines.append(f"{escape(first_buff.name)} · {escape(first_buff.remaining)}")
        if len(character.active_buffs) > 1:
            lines.append(f"Ещё эффектов: {len(character.active_buffs) - 1}")
    return "\n".join(lines)


def render_character_section(title: str, description: str) -> str:
    return f"{title}\n\n{description}\n\n<i>Экран открыт в том же сообщении.</i>"
