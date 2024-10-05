# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc
from typing import Optional, Any, Dict


from .config import LdapProducerSettings


class MessageQueuePort(abc.ABC):
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        self.settings = settings

    @abc.abstractmethod
    async def __aenter__(self):
        pass

    @abc.abstractmethod
    async def __aexit__(self, *args):
        pass

    @abc.abstractmethod
    async def enqueue_change_event(self, new: Dict[str, Any], old: Dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    async def ensure_queue_exists(self) -> None:
        pass
