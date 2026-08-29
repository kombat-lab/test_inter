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
        claimable_quests=1,
        active_buffs=(
            ActiveBuff(
                icon="🔮",
                name="Благословение тумана",
                remaining_seconds=416 * 60 * 60 + 28 * 60 + 46,
                effects=(
                    "Лут +30%",
                    "Пыль +30%",
                    "XP +30%",
                ),
            ),
            ActiveBuff(
                icon="💍",
                name="Серьга дропа (30 дней)",
                remaining_seconds=29 * 24 * 60 * 60 + 23 * 60 * 60 + 59 * 60,
                effects=("Лут +15%",),
            ),
            ActiveBuff(
                icon="💍",
                name="Серьга дропа (30 дней)",
                remaining_seconds=29 * 24 * 60 * 60 + 23 * 60 * 60 + 59 * 60,
                effects=("Лут +15%",),
            ),
        ),
    )
