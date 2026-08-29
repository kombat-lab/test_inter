from __future__ import annotations

from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class CharacterSection(StrEnum):
    OVERVIEW = "overview"
    EFFECTS = "effects"
    QUESTS = "quests"
    INVENTORY = "inventory"
    STATS = "stats"
    SKILLS = "skills"
    EQUIPMENT = "equipment"


class CharacterCallback(CallbackData, prefix="character"):
    section: CharacterSection
