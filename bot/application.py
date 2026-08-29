from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.config import Settings
from bot.handlers import register_routers
from bot.logging import configure_logging

logger = logging.getLogger(__name__)


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    register_routers(dispatcher)
    return dispatcher


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть главное меню"),
            BotCommand(command="character", description="Открыть персонажа"),
            BotCommand(command="help", description="Помощь"),
        ]
    )


async def run_bot() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = create_dispatcher()

    try:
        bot_info = await bot.get_me()
        await _set_commands(bot)
        await bot.delete_webhook(drop_pending_updates=settings.drop_pending_updates)
        logger.info("Starting @%s in long-polling mode", bot_info.username)
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    finally:
        await bot.session.close()
        logger.info("Bot stopped")
