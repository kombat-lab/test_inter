from __future__ import annotations

from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from bot.callbacks.character import CharacterCallback, CharacterSection
from bot.keyboards.character import character_keyboard
from bot.services.characters import get_character
from bot.views.character import render_character_caption

router = Router(name=__name__)

_CHARACTER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "character.png"
_SECTION_NOTICES = {
    CharacterSection.QUESTS: "Раздел «Квесты» будет подключён следующим этапом.",
    CharacterSection.INVENTORY: "Раздел «Инвентарь» будет подключён следующим этапом.",
    CharacterSection.STATS: "Раздел «Характеристики» будет подключён следующим этапом.",
    CharacterSection.SKILLS: "Раздел «Приемы» будет подключён следующим этапом.",
    CharacterSection.EQUIPMENT: "Раздел «Экипировка» будет подключён следующим этапом.",
}


async def send_character_screen(message: Message) -> None:
    character = get_character()
    await message.answer_photo(
        photo=FSInputFile(_CHARACTER_IMAGE),
        caption=render_character_caption(character),
        reply_markup=character_keyboard(),
    )


@router.message(Command("character"))
async def handle_character_command(message: Message) -> None:
    await send_character_screen(message)


@router.callback_query(CharacterCallback.filter())
async def handle_character_section(
    callback: CallbackQuery,
    callback_data: CharacterCallback,
) -> None:
    await callback.answer(_SECTION_NOTICES[callback_data.section], show_alert=True)
