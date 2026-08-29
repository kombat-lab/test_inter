from __future__ import annotations

from html import escape

from bot.models.character import ActiveBuff, Character

_PROGRESS_SEGMENTS = 10
_WORD_JOINER = "\u2060"


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _render_progress(character: Character) -> tuple[str, int]:
    if character.experience_to_next_level <= 0:
        return _WORD_JOINER.join(["⬛️"] * _PROGRESS_SEGMENTS), 0

    ratio = min(character.experience / character.experience_to_next_level, 1.0)
    percentage = round(ratio * 100)
    filled = round(ratio * _PROGRESS_SEGMENTS)
    if percentage < 35:
        filled_segment = "🟧"
    elif percentage < 70:
        filled_segment = "🟨"
    else:
        filled_segment = "🟩"
    segments = [filled_segment] * filled + ["⬛️"] * (_PROGRESS_SEGMENTS - filled)
    bar = _WORD_JOINER.join(segments)
    return bar, percentage


def _format_duration(seconds: int) -> str:
    seconds = max(seconds, 0)
    days, remainder = divmod(seconds, 24 * 60 * 60)
    hours, remainder = divmod(remainder, 60 * 60)
    minutes, seconds = divmod(remainder, 60)

    if days:
        return f"{days}д {hours}ч" if hours else f"{days}д"
    if hours:
        return f"{hours}ч {minutes}м" if minutes else f"{hours}ч"
    if minutes:
        return f"{minutes}м {seconds}с" if seconds else f"{minutes}м"
    return f"{seconds}с"


def _group_buffs(buffs: tuple[ActiveBuff, ...]) -> list[tuple[ActiveBuff, int]]:
    grouped: list[tuple[ActiveBuff, int]] = []
    indexes: dict[ActiveBuff, int] = {}
    for buff in buffs:
        if buff in indexes:
            index = indexes[buff]
            grouped[index] = (buff, grouped[index][1] + 1)
        else:
            indexes[buff] = len(grouped)
            grouped.append((buff, 1))
    return grouped


def _buff_title(buff: ActiveBuff, count: int) -> str:
    suffix = f" ×{count}" if count > 1 else ""
    return f"{escape(buff.icon)} {escape(buff.name)}{suffix}"


def _render_buff(buff: ActiveBuff, count: int) -> list[str]:
    title = _buff_title(buff, count)
    remaining = _format_duration(buff.remaining_seconds)
    effects = " · ".join(escape(effect) for effect in buff.effects)

    return [f"<b>{title}</b> · {remaining}", f"└ {effects}"]


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
        progress,
        f"{_format_number(character.experience)} / "
        f"{_format_number(character.experience_to_next_level)} XP",
        "",
        f"✨ Пыль: <b>{_format_number(character.mist_dust)}</b>",
        f"💎 Кристаллы: <b>{_format_number(character.mist_crystals)}</b>",
        "",
        f"⚡ <b>Эффекты · {len(character.active_buffs)}</b>",
    ]
    grouped_buffs = _group_buffs(character.active_buffs)
    if expanded_buffs:
        for buff, count in grouped_buffs:
            lines.append("")
            lines.extend(_render_buff(buff, count))
    else:
        for buff, count in grouped_buffs:
            lines.append(f"{_buff_title(buff, count)} · {_format_duration(buff.remaining_seconds)}")
    return "\n".join(lines)


def render_character_section(title: str, description: str) -> str:
    return f"{title}\n\n{description}\n\n<i>Экран открыт в том же сообщении.</i>"
