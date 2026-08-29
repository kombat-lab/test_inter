from __future__ import annotations

from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class EquipmentAction(StrEnum):
    HOME = "home"
    MODE = "mode"
    GROUP = "group"
    SLOT = "slot"


class EquipmentCallback(CallbackData, prefix="equipment"):
    action: EquipmentAction
    value: str = ""
