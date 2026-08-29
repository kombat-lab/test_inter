from __future__ import annotations

from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, InputMediaPhoto, Message

from bot.callbacks.character import CharacterCallback, CharacterSection
from bot.keyboards.character import character_back_keyboard, character_keyboard
from bot.services.characters import get_character
from bot.views.character import render_character_caption, render_character_section

router = Router(name=__name__)

_CHARACTER_IMAGE = Path(__file__).resolve().parents[1] / "assets" / "character.png"
_SECTION_CONTENT = {
    CharacterSection.QUESTS: (
        "📜 <b>Квесты</b>",
        "Здесь появятся активные задания, награды и прогресс прохождения.",
    ),
    CharacterSection.INVENTORY: (
        "🎒 <b>Инвентарь</b>",
        "Здесь появятся предметы, расходники и материалы персонажа.",
    ),
    CharacterSection.STATS: (
        "📊 <b>Характеристики</b>",
        "Здесь появятся боевые параметры и подробные бонусы персонажа.",
    ),
    CharacterSection.SKILLS: (
        "⚔️ <b>Приёмы</b>",
        "Здесь появятся изученные приёмы и настройка боевого набора.",
    ),
    CharacterSection.EQUIPMENT: (
        "🛡 <b>Экипировка</b>",
        "Здесь появятся надетые предметы и доступные улучшения.",
    ),
}


async def send_character_screen(message: Message) -> None:
    character = get_character()
    await message.answer_photo(
        photo=FSInputFile(_CHARACTER_IMAGE),
        caption=render_character_caption(character),
        reply_markup=character_keyboard(),
    )


async def edit_character_screen(message: Message) -> None:
    character = get_character()
    await message.edit_media(
        media=InputMediaPhoto(
            media=FSInputFile(_CHARACTER_IMAGE),
            caption=render_character_caption(character),
        ),
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
    await callback.answer()
    if not isinstance(callback.message, Message):
        return

    character = get_character()
    match callback_data.section:
        case CharacterSection.OVERVIEW:
            await callback.message.edit_caption(
                caption=render_character_caption(character),
                reply_markup=character_keyboard(),
            )
        case CharacterSection.EFFECTS:
            await callback.message.edit_caption(
                caption=render_character_caption(character, expanded_buffs=True),
                reply_markup=character_keyboard(effects_expanded=True),
            )
        case _:
            title, description = _SECTION_CONTENT[callback_data.section]
            await callback.message.edit_caption(
                caption=render_character_section(title, description),
                reply_markup=character_back_keyboard(),
            )
