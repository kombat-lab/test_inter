from __future__ import annotations

from html import escape

from bot.models.stats import CharacterStats


def render_stats_caption(stats: CharacterStats, *, expanded: bool = False) -> str:
    lines = [
        "📊 <b>Характеристики</b>",
        f"🧙 {escape(stats.combat_class)} · Путь {escape(stats.path)} · {stats.level} уровень",
        "",
        f"❤️ <b>{stats.health} / {stats.max_health} HP</b>",
        f"🗡 Урон <b>{stats.physical_damage}</b>  ·  🔮 Маг. урон <b>{stats.magic_damage}</b>",
        "",
        "<b>Основные параметры</b>",
        f"💪 Сила <b>{stats.strength}</b>  ·  💨 Ловкость <b>{stats.dexterity}</b>",
        f"🧠 Интеллект <b>{stats.intelligence}</b>  ·  ❤️‍🩹 Выносливость <b>{stats.endurance}</b>",
        f"🍀 Удача <b>{stats.luck}</b>",
        "",
        "<b>Защита</b>",
        f"🛡 Защита <b>{stats.defense}</b>  ·  🪬 Маг. защита <b>{stats.magic_defense}</b>",
        f"🧱 Снижение урона <b>{stats.damage_reduction:.1f}%</b>",
    ]
    if expanded:
        lines.extend(
            [
                "",
                "<b>Боевые показатели</b>",
                f"⚔️ Атака <b>{stats.attack}</b>  ·  🔮 Маг. атака <b>{stats.magic_attack}</b>",
                f"💢 Крит <b>{stats.critical}</b>  ·  "
                f"Сила крита <b>{stats.critical_power:.1f}%</b>",
                f"🧱 Блок <b>{stats.block}</b>  ·  ⚡ Инициатива <b>{stats.initiative}</b>",
                "",
                "<b>Особые показатели</b>",
                f"🍀 Ид. крит <b>{stats.identity_critical}</b>  ·  "
                f"🌪 Ид. уворот <b>{stats.identity_dodge}</b>",
                f"🐾 Скорость передвижения <b>+{stats.movement_speed:.1f}%</b>",
            ]
        )
    lines.extend(["", f"🔘 Свободные очки: <b>{stats.free_points}</b>"])
    return "\n".join(lines)
