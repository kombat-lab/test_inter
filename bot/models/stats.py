from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CharacterStats:
    combat_class: str
    path: str
    level: int
    health: int
    max_health: int
    physical_damage: str
    magic_damage: str
    strength: int
    dexterity: int
    intelligence: int
    endurance: int
    luck: int
    defense: int
    magic_defense: int
    damage_reduction: float
    critical: int
    critical_power: float
    block: int
    attack: int
    magic_attack: int
    identity_critical: int
    identity_dodge: int
    initiative: int
    movement_speed: float
    free_points: int
