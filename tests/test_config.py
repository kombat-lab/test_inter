from __future__ import annotations

import pytest

from bot.config import ConfigurationError, Settings

_ENVIRONMENT_VARIABLES = (
    "BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "LOG_LEVEL",
    "DROP_PENDING_UPDATES",
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in _ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(variable, raising=False)


def test_settings_reads_bothost_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "test-token")

    settings = Settings.from_env()

    assert settings.bot_token == "test-token"
    assert settings.log_level == "INFO"
    assert settings.drop_pending_updates is False


def test_settings_accepts_telegram_token_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "alias-token")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("DROP_PENDING_UPDATES", "yes")

    settings = Settings.from_env()

    assert settings.bot_token == "alias-token"
    assert settings.log_level == "DEBUG"
    assert settings.drop_pending_updates is True


def test_settings_requires_token() -> None:
    with pytest.raises(ConfigurationError, match="BOT_TOKEN"):
        Settings.from_env()


def test_settings_rejects_invalid_boolean(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "test-token")
    monkeypatch.setenv("DROP_PENDING_UPDATES", "sometimes")

    with pytest.raises(ConfigurationError, match="DROP_PENDING_UPDATES"):
        Settings.from_env()
