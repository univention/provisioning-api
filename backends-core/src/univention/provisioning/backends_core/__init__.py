# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from .key_value_db import KeyValueDB
from .message_queue import MessageQueue
from .nats_kv import NatsKeyValueDB
from .nats_mq import NatsMessageQueue

__all__ = ["key_value_store", "message_queue"]


def key_value_store(server: str, user: str, password: str) -> KeyValueDB:
    return NatsKeyValueDB(server=server, user=user, password=password)


def message_queue(
    server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs
) -> MessageQueue:
    return NatsMessageQueue(
        server=server, user=user, password=password, max_reconnect_attempts=max_reconnect_attempts, **connect_kwargs
    )
