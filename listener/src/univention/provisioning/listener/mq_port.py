# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Protocol, Self, runtime_checkable


@runtime_checkable
class ListenerMessageQueuePort(Protocol):
    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool: ...

    async def enqueue_change_event(
        self,
        new: dict[str, Any],
        old: dict[str, Any],
    ) -> None: ...

    async def ensure_queue_exists(self) -> None: ...
