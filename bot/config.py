from __future__ import annotations

import os
from dataclasses import dataclass, field


class ConfigurationError(RuntimeError):
    """Raised when the bot cannot start because configuration is invalid."""


_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})
_LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})


def _read_bool(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    value = raw_value.strip().lower()
    if value in _TRUE_VALUES:
        return True
    if value in _FALSE_VALUES:
        return False
    raise ConfigurationError(
        f"Переменная {name} должна быть одной из: "
        "true/false, yes/no, on/off или 1/0."
    )


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str = field(repr=False)
    log_level: str = "INFO"
    drop_pending_updates: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        token = (os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
        if not token:
            raise ConfigurationError(
                "Не найден токен Telegram-бота. Задайте переменную окружения BOT_TOKEN."
            )

        log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
        if log_level not in _LOG_LEVELS:
            raise ConfigurationError(
                "Переменная LOG_LEVEL должна быть одной из: "
                "DEBUG, INFO, WARNING, ERROR, CRITICAL."
            )

        return cls(
            bot_token=token,
            log_level=log_level,
            drop_pending_updates=_read_bool("DROP_PENDING_UPDATES", default=False),
        )
