# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from abc import ABC, abstractmethod

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from shared.models import Message


class Sink(ABC):
    """A sink is the consumer of a message queue."""

    def __init__(self):
        pass

    @abstractmethod
    async def open(self):
        """Open/accept the connection to/with the remote end."""
        pass

    async def send_message(self, message: Message):
        """Send a message to the remote end."""
        await self.send(message.model_dump_json())

    @abstractmethod
    async def send(self, message: str):
        """Send a message to the remote end."""
        pass

    @abstractmethod
    async def close(self):
        """Close connection with remote end."""
        pass


class WebSocketSink(Sink):
    """A consumer connected to a message queue via a WebSocket."""

    def __init__(self, websocket: WebSocket):
        super().__init__()
        self.websocket = websocket

    def _is_connected(self):
        return (
            self.websocket.application_state == WebSocketState.CONNECTED
            and self.websocket.client_state == WebSocketState.CONNECTED
        )

    async def open(self):
        """Open a connection with the remote end."""
        await self.websocket.accept()

    async def send(self, message: str):
        """Send a message to the remote end."""
        if self._is_connected():
            await self.websocket.send_text(message)

    async def close(self):
        """Close connection with remote end."""
        if self._is_connected():
            try:
                await self.websocket.close()
            except Exception:
                # if connection was already closed by the remote end,
                # there is nothing we can do
                pass


class SinkManager:
    """A manager for all consumers currently connected to the dispatcher."""

    def __init__(self):
        self.sinks: dict[str, Sink] = {}

    async def add(self, subscriber_name: str, sink: Sink) -> Sink:
        """Manage a new `sink` with the given `subscriber_name`.

        If a sink with this `subscriber_name` is already present,
        it will be disconnected first.
        """
        if old_sink := self.sinks.get(subscriber_name):
            await old_sink.close()

        self.sinks[subscriber_name] = sink
        await self.sinks[subscriber_name].open()

        return sink

    async def close(self, subscriber_name: str):
        """Close the connection with the given `subscriber_name`."""
        if sink := self.sinks.get(subscriber_name):
            await sink.close()
            self.sinks.pop(subscriber_name)
