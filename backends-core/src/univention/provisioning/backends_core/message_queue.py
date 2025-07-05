# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


from typing import Any, Callable, Coroutine, NamedTuple, Protocol, runtime_checkable


class Empty(Exception): ...


class Acknowledgements(NamedTuple):
    acknowledge_message: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_negatively: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]


@runtime_checkable
class MessageQueuePort(Protocol):
    """
    Abstract port for an asynchronous message queue.
    """

    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def add_message(
        self,
        stream: str,
        subject: str,
        payload: bytes,
    ) -> None: ...

    async def ensure_stream(
        self,
        stream: str,
        manual_delete: bool,
        subjects: list[str] | None = None,
    ) -> None: ...
