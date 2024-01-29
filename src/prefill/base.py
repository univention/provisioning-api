# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc

from consumer.messages.service.messages import MessageService


class PreFillService(abc.ABC):
    def __init__(self, service: MessageService, subscriber_name: str, topic: str):
        self._service = service
        self._subscriber_name = subscriber_name
        self._topic = topic

    @abc.abstractmethod
    async def fetch(self):
        pass
