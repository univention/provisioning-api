from typing import List, Tuple, Dict, Optional
from typing_extensions import Self
from abc import ABC, abstractmethod

from core.models import Message
from core.models.queue import MQMessage


class BaseMessageQueue(ABC):
    """The base class for message queue adapters."""

    @abstractmethod
    async def add_message(self, subscriber_name: str, message: Message):
        """Publish a message to a subscription subject."""
        pass

    @abstractmethod
    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        """Retrieve multiple messages by subscription subject."""
        pass

    @abstractmethod
    async def delete_message(self, msg: MQMessage):
        """Delete a message from a message queue stream."""
        pass

    @abstractmethod
    async def delete_stream(self, subscriber_name: str):
        """Delete the stream for a given subject from the message queue."""
        pass


class BaseKVStore(ABC):
    """The base class for key-value store adapters."""

    @abstractmethod
    async def add_live_message(self, subscriber_name: str, message: Message):
        pass

    @abstractmethod
    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """TODO: Add a message to the prefill queue."""
        pass

    @abstractmethod
    async def delete_prefill_messages(self, subscriber_name: str):
        """TODO: Remove a message from the prefill queue."""
        pass

    @abstractmethod
    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[List[Tuple[str, Message]]]:
        pass

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ):
        pass

    async def delete_message(self, subscriber_name: str, message_id: str):
        pass

    async def delete_queue(self, subscriber_name: str):
        pass

    async def get_subscriber_names(self):
        pass

    async def get_subscriber_by_name(self, name: str):
        pass

    async def get_subscriber_info(self, name: str):
        pass

    async def get_subscriber_topics(self, name: str):
        pass

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        pass

    async def get_subscriber_queue_status(self, name: str):
        pass

    async def set_subscriber_queue_status(self, name: str, status: str):
        pass

    async def delete_subscriber(self, name: str):
        pass
