from __future__ import annotations

from contextlib import suppress
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message

from bot.callbacks.inventory import InventoryAction, InventoryCallback
from bot.keyboards.inventory import (
    inventory_filters_keyboard,
    inventory_item_keyboard,
    inventory_keyboard,
    inventory_quantity_keyboard,
    inventory_search_keyboard,
)
from bot.models.inventory import InventoryItem, ItemCategory
from bot.services.characters import get_character
from bot.services.inventory import (
    InventoryOperationError,
    get_category_counts,
    get_inventory_page,
    get_item,
    is_equipped,
    toggle_equipped,
    use_item,
)
from bot.services.message_edits import (
    safe_bot_edit_caption,
    safe_edit_caption,
    safe_edit_media,
)
from bot.states.inventory import InventorySearch
from bot.views.inventory import (
    render_filter_caption,
    render_inventory_caption,
    render_item_caption,
    render_search_prompt,
)

router = Router(name=__name__)

_INVENTORY_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "inventory-hero.png"
_CATEGORY_KEY = "inventory_category"
_PAGE_KEY = "inventory_page"
_QUERY_KEY = "inventory_query"
_MESSAGE_ID_KEY = "inventory_message_id"
_CHAT_ID_KEY = "inventory_chat_id"


async def _get_view_state(state: FSMContext) -> tuple[ItemCategory, int, str]:
    data = await state.get_data()
    try:
        category = ItemCategory(data.get(_CATEGORY_KEY, ItemCategory.ALL.value))
    except ValueError:
        category = ItemCategory.ALL
    return category, int(data.get(_PAGE_KEY, 0)), str(data.get(_QUERY_KEY, ""))


async def _store_view_state(
    state: FSMContext, *, category: ItemCategory, page: int, query: str, message: Message
) -> None:
    await state.update_data(
        {
            _CATEGORY_KEY: category.value,
            _PAGE_KEY: page,
            _QUERY_KEY: query,
            _MESSAGE_ID_KEY: message.message_id,
            _CHAT_ID_KEY: message.chat.id,
        }
    )


async def _edit_inventory_list(
    message: Message,
    user_id: int,
    state: FSMContext,
    *,
    category: ItemCategory,
    page: int = 0,
    query: str = "",
) -> None:
    inventory = get_inventory_page(user_id, category=category, query=query, page=page)
    await _store_view_state(
        state, category=category, page=inventory.page, query=query, message=message
    )
    await safe_edit_caption(
        message,
        caption=render_inventory_caption(inventory, get_character(), category, query=query),
        reply_markup=inventory_keyboard(inventory, category, query=query),
    )


async def open_inventory_screen(message: Message, user_id: int, state: FSMContext) -> None:
    await state.clear()
    category = ItemCategory.ALL
    inventory = get_inventory_page(user_id, category=category)
    await _store_view_state(
        state, category=category, page=inventory.page, query="", message=message
    )
    await safe_edit_media(
        message,
        media=InputMediaPhoto(
            media=FSInputFile(_INVENTORY_IMAGE),
            caption=render_inventory_caption(inventory, get_character(), category),
        ),
        reply_markup=inventory_keyboard(inventory, category),
    )


async def send_inventory_screen(message: Message, user_id: int, state: FSMContext) -> None:
    await state.clear()
    category = ItemCategory.ALL
    inventory = get_inventory_page(user_id, category=category)
    sent_message = await message.answer_photo(
        photo=FSInputFile(_INVENTORY_IMAGE),
        caption=render_inventory_caption(inventory, get_character(), category),
        reply_markup=inventory_keyboard(inventory, category),
    )
    await _store_view_state(
        state, category=category, page=inventory.page, query="", message=sent_message
    )


async def _show_item(
    message: Message, user_id: int, item: InventoryItem, *, notice: str = ""
) -> None:
    equipped = is_equipped(user_id, item)
    await safe_edit_caption(
        message,
        caption=render_item_caption(item, equipped=equipped, notice=notice),
        reply_markup=inventory_item_keyboard(item, equipped=equipped),
    )


@router.message(Command("inventory"))
async def handle_inventory_command(message: Message, state: FSMContext) -> None:
    if message.from_user:
        await send_inventory_screen(message, message.from_user.id, state)


@router.callback_query(InventoryCallback.filter())
async def handle_inventory_callback(
    callback: CallbackQuery, callback_data: InventoryCallback, state: FSMContext
) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return

    message = callback.message
    user_id = callback.from_user.id
    action = callback_data.action
    value = callback_data.value
    category, page, query = await _get_view_state(state)

    if action is InventoryAction.PAGE:
        await callback.answer()
        await _edit_inventory_list(
            message, user_id, state, category=category, page=int(value), query=query
        )
    elif action is InventoryAction.REFRESH:
        await callback.answer("Инвентарь обновлён")
        await _edit_inventory_list(
            message, user_id, state, category=category, page=page, query=query
        )
    elif action is InventoryAction.FILTERS:
        await callback.answer()
        await safe_edit_caption(
            message,
            caption=render_filter_caption(category),
            reply_markup=inventory_filters_keyboard(get_category_counts(user_id), category),
        )
    elif action is InventoryAction.CATEGORY:
        await callback.answer()
        await state.set_state(None)
        await _edit_inventory_list(message, user_id, state, category=ItemCategory(value))
    elif action in {InventoryAction.BACK_LIST, InventoryAction.CANCEL_SEARCH}:
        await callback.answer()
        await state.set_state(None)
        await _edit_inventory_list(
            message, user_id, state, category=category, page=page, query=query
        )
    elif action is InventoryAction.SEARCH:
        await callback.answer()
        await _store_view_state(state, category=category, page=page, query=query, message=message)
        await state.set_state(InventorySearch.waiting_for_query)
        await safe_edit_caption(
            message, caption=render_search_prompt(), reply_markup=inventory_search_keyboard()
        )
    elif action is InventoryAction.CLEAR_SEARCH:
        await callback.answer("Поиск сброшен")
        await _edit_inventory_list(message, user_id, state, category=ItemCategory.ALL)
    else:
        await _handle_item_action(callback, callback_data)


async def _handle_item_action(callback: CallbackQuery, callback_data: InventoryCallback) -> None:
    if not isinstance(callback.message, Message):
        await callback.answer()
        return
    user_id = callback.from_user.id
    value = callback_data.value
    item = get_item(user_id, value.split(".", maxsplit=1)[0])
    if item is None:
        await callback.answer("Предмет больше недоступен", show_alert=True)
        return

    if callback_data.action is InventoryAction.ITEM:
        await callback.answer()
        await _show_item(callback.message, user_id, item)
    elif callback_data.action is InventoryAction.USE_MENU:
        await callback.answer()
        await safe_edit_caption(
            callback.message,
            caption=render_item_caption(item, equipped=is_equipped(user_id, item)),
            reply_markup=inventory_quantity_keyboard(item),
        )
    elif callback_data.action is InventoryAction.USE:
        try:
            _, raw_quantity = value.rsplit(".", maxsplit=1)
            used_quantity = int(raw_quantity)
            item = use_item(user_id, item.item_id, used_quantity)
        except (InventoryOperationError, ValueError) as error:
            await callback.answer(str(error), show_alert=True)
            return
        await callback.answer(f"Использовано: {used_quantity}")
        await _show_item(
            callback.message, user_id, item, notice=f"Использовано: {used_quantity} шт."
        )
    elif callback_data.action is InventoryAction.EQUIP:
        try:
            equipped = toggle_equipped(user_id, item.item_id)
        except InventoryOperationError as error:
            await callback.answer(str(error), show_alert=True)
            return
        await callback.answer("Предмет надет" if equipped else "Предмет снят")
        await _show_item(
            callback.message,
            user_id,
            item,
            notice="Предмет надет." if equipped else "Предмет снят.",
        )


@router.message(InventorySearch.waiting_for_query, F.text & ~F.text.startswith("/"))
async def handle_inventory_search(message: Message, state: FSMContext) -> None:
    if message.from_user is None or message.text is None:
        return
    query = " ".join(message.text.split())[:40]
    if not query:
        await message.answer("Введите хотя бы один символ.")
        return

    data = await state.get_data()
    message_id = data.get(_MESSAGE_ID_KEY)
    chat_id = data.get(_CHAT_ID_KEY)
    await state.set_state(None)
    if not isinstance(message_id, int) or not isinstance(chat_id, int):
        await send_inventory_screen(message, message.from_user.id, state)
        return

    category = ItemCategory.ALL
    inventory = get_inventory_page(message.from_user.id, query=query)
    await state.update_data(
        {
            _CATEGORY_KEY: category.value,
            _PAGE_KEY: inventory.page,
            _QUERY_KEY: query,
            _MESSAGE_ID_KEY: message_id,
            _CHAT_ID_KEY: chat_id,
        }
    )
    await safe_bot_edit_caption(
        message.bot,
        chat_id=chat_id,
        message_id=message_id,
        caption=render_inventory_caption(inventory, get_character(), category, query=query),
        reply_markup=inventory_keyboard(inventory, category, query=query),
    )
    with suppress(TelegramBadRequest):
        await message.delete()
