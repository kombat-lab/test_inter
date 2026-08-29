from __future__ import annotations

from bot.models.stats import CharacterStats


def render_stats_caption(stats: CharacterStats, *, expanded: bool = False) -> str:
    lines = [
        "📊 <b>Характеристики</b>",
        "",
        f"❤️ <b>{stats.health} / {stats.max_health} HP</b>",
        f"🗡 Урон <b>{stats.physical_damage}</b>  ·  🔮 Маг. урон <b>{stats.magic_damage}</b>",
        "",
        "<b>Основные параметры</b>",
        f"💪 <b>{stats.strength}</b> · 💨 <b>{stats.dexterity}</b> · "
        f"🧠 <b>{stats.intelligence}</b> · ❤️‍🩹 <b>{stats.endurance}</b> · "
        f"🍀 <b>{stats.luck}</b>",
        "",
        "<b>Защита</b>",
        f"🛡 <b>{stats.defense}</b> · 🪬 <b>{stats.magic_defense}</b> · "
        f"🧱 <b>{stats.damage_reduction:.1f}%</b>",
        "",
        "<b>Второстепенные параметры</b>",
        f"💢 Крит <b>{stats.critical}</b> · "
        f"🍀 Ид. крит <b>{stats.identity_critical}</b> · "
        f"🌪 Ид. уворот <b>{stats.identity_dodge}</b>",
        f"⚡ Инициатива <b>{stats.initiative}</b> · "
        f"🐾 Скорость <b>+{stats.movement_speed:.1f}%</b>",
    ]
    if expanded:
        lines.extend(
            [
                "",
                "<b>Дополнительные боевые показатели</b>",
                f"⚔️ Атака <b>{stats.attack}</b>  ·  🔮 Маг. атака <b>{stats.magic_attack}</b>",
                f"💢 Сила крита <b>{stats.critical_power:.1f}%</b>  ·  "
                f"🧱 Блок <b>{stats.block}</b>",
            ]
        )
    lines.extend(["", f"🔘 Свободные очки: <b>{stats.free_points}</b>"])
    return "\n".join(lines)
