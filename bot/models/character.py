from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActiveBuff:
    icon: str
    name: str
    remaining_seconds: int
    effects: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Character:
    name: str
    level: int
    experience: int
    experience_to_next_level: int
    mist_dust: int
    mist_crystals: int
    combat_class: str
    path: str
    active_buffs: tuple[ActiveBuff, ...] = ()
    claimable_quests: int = 0
