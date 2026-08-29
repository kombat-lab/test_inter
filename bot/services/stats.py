from __future__ import annotations

from bot.models.stats import CharacterStats


def get_character_stats() -> CharacterStats:
    """Return reference stats until persistent player storage is connected."""
    return CharacterStats(
        combat_class="Аколит",
        path="Аколит",
        level=18,
        health=750,
        max_health=750,
        physical_damage="1",
        magic_damage="74–80",
        strength=1,
        dexterity=1,
        intelligence=56,
        endurance=38,
        luck=6,
        defense=61,
        magic_defense=58,
        damage_reduction=10.6,
        critical=3,
        critical_power=5.0,
        block=8,
        attack=1,
        magic_attack=67,
        identity_critical=1,
        identity_dodge=1,
        initiative=50,
        movement_speed=15.0,
        free_points=0,
    )
