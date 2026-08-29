from __future__ import annotations

import asyncio
from dataclasses import dataclass

from bot.services.message_edits import safe_edit_caption


@dataclass
class _Chat:
    id: int


class _Message:
    def __init__(self) -> None:
        self.chat = _Chat(id=1)
        self.message_id = 2
        self.active_edits = 0
        self.max_active_edits = 0

    async def edit_caption(self, **_kwargs: object) -> None:
        self.active_edits += 1
        self.max_active_edits = max(self.max_active_edits, self.active_edits)
        await asyncio.sleep(0)
        self.active_edits -= 1


def test_message_edits_are_serialized() -> None:
    async def run_edits() -> int:
        message = _Message()
        await asyncio.gather(
            safe_edit_caption(message, caption="one", reply_markup=None),
            safe_edit_caption(message, caption="two", reply_markup=None),
        )
        return message.max_active_edits

    assert asyncio.run(run_edits()) == 1
