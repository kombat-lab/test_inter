from __future__ import annotations

from aiogram import Router
from aiogram.types import BufferedInputFile, CallbackQuery, InputMediaPhoto, Message

from bot.callbacks.equipment import EquipmentAction, EquipmentCallback
from bot.keyboards.equipment import (
    equipment_group_keyboard,
    equipment_keyboard,
    equipped_slot_keyboard,
)
from bot.models.equipment import EquipmentGroup
from bot.services.equipment import (
    get_equipment_loadout,
    get_equipped_slot,
    get_group_slots,
)
from bot.services.message_edits import safe_edit_caption, safe_edit_media
from bot.views.equipment import (
    render_equipment_caption,
    render_equipment_group_caption,
    render_equipped_slot_caption,
)
from bot.views.equipment_image import render_equipment_board

router = Router(name=__name__)


async def open_equipment_screen(
    message: Message,
    user_id: int,
) -> None:
    loadout = get_equipment_loadout(user_id)
    image = BufferedInputFile(
        render_equipment_board(loadout),
        filename="equipment-stats.jpg",
    )
    await safe_edit_media(
        message,
        media=InputMediaPhoto(
            media=image,
            caption=render_equipment_caption(loadout),
        ),
        reply_markup=equipment_keyboard(loadout),
    )


@router.callback_query(EquipmentCallback.filter())
async def handle_equipment_callback(
    callback: CallbackQuery,
    callback_data: EquipmentCallback,
) -> None:
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    user_id = callback.from_user.id
    match callback_data.action:
        case EquipmentAction.HOME:
            await open_equipment_screen(callback.message, user_id)
        case EquipmentAction.MODE:
            # Compatibility with buttons on messages sent by the previous UI.
            await open_equipment_screen(callback.message, user_id)
        case EquipmentAction.GROUP:
            group = EquipmentGroup(callback_data.value)
            slots = get_group_slots(user_id, group)
            await safe_edit_caption(
                callback.message,
                caption=render_equipment_group_caption(group, slots),
                reply_markup=equipment_group_keyboard(group, slots),
            )
        case EquipmentAction.SLOT:
            slot = get_equipped_slot(user_id, callback_data.value)
            if slot is None:
                return
            await safe_edit_caption(
                callback.message,
                caption=render_equipped_slot_caption(slot),
                reply_markup=equipped_slot_keyboard(slot),
            )
