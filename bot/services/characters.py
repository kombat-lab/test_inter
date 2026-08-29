from __future__ import annotations

from bot.models.character import ActiveBuff, Character


def get_character() -> Character:
    """Return reference data until persistent player storage is connected."""
    return Character(
        name="Kombat",
        level=18,
        experience=212_435,
        experience_to_next_level=238_650,
        mist_dust=70_258,
        mist_crystals=213,
        combat_class="Аколит",
        path="Аколит",
        active_buffs=(
            ActiveBuff(
                name="Благословение тумана",
                remaining="416ч 28м 46с",
                effects=(
                    "шанс лута +30.0%",
                    "туманная пыль (ед.) +30.0%",
                    "XP +30.0%",
                ),
            ),
            ActiveBuff(
                name="Серьга дропа (30 дней)",
                remaining="29д 23ч 59м",
                effects=("Шанс лута +15%",),
                inline=True,
            ),
            ActiveBuff(
                name="Серьга дропа (30 дней)",
                remaining="29д 23ч 59м",
                effects=("Шанс лута +15%",),
                inline=True,
            ),
        ),
    )
