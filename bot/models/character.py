from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActiveBuff:
    name: str
    remaining: str
    effects: tuple[str, ...]
    inline: bool = False


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
