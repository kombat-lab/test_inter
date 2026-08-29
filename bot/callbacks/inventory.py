from __future__ import annotations

from enum import StrEnum

from aiogram.filters.callback_data import CallbackData


class InventoryAction(StrEnum):
    NOOP = "noop"
    PAGE = "page"
    ITEM = "item"
    FILTERS = "filters"
    CATEGORY = "category"
    SEARCH = "search"
    CLEAR_SEARCH = "clear_search"
    CANCEL_SEARCH = "cancel_search"
    REFRESH = "refresh"
    BACK_LIST = "back_list"
    USE_MENU = "use_menu"
    USE = "use"
    EQUIP = "equip"
    COMPARE = "compare"


class InventoryCallback(CallbackData, prefix="inventory"):
    action: InventoryAction
    value: str = ""
