# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional, Self

import msgpack
from nats.aio.client import Client as NATS
from nats.js.api import RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError
from pydantic import BaseModel, Field, root_validator
from pydantic.json import pydantic_encoder

from .config import LdapProducerSettings, ldap_producer_settings
from .mq_port import MessageQueuePort

logger = logging.getLogger(__name__)

LDAP_SUBJECT = "ldap-producer-subject"
LDAP_PRODUCER_QUEUE_NAME = "ldap-producer"

LDAP_OBJECT_TYPE_FIELD = "univentionObjectType"
UDM_OBJECT_TYPE_FIELD = "objectType"


class EmptyBodyError(Exception): ...


class NoUDMTypeError(Exception): ...


class PublisherName(str, Enum):
    udm_listener = "udm-listener"
    ldif_producer = "ldif-producer"
    udm_pre_fill = "udm-pre-fill"
    consumer_registration = "consumer-registration"
    consumer_client_test = "consumer_client_test"


class Body(BaseModel):
    old: Dict[str, Any] = Field(description="The LDAP/UDM object before the change.")
    new: Dict[str, Any] = Field(description="The LDAP/UDM object after the change.")

    @root_validator
    def check_not_both_empty(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("old") and not values.get("new"):
            raise EmptyBodyError("old' and 'new' cannot be both empty.")
        return values

    @root_validator
    def check_has_udm_object_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if LDAP_OBJECT_TYPE_FIELD in values.get("new") or LDAP_OBJECT_TYPE_FIELD in values.get("old"):
            obj_type = LDAP_OBJECT_TYPE_FIELD
        else:
            obj_type = UDM_OBJECT_TYPE_FIELD
        if not values.get("new").get(obj_type) and not values.get("old").get(obj_type):
            raise NoUDMTypeError("No UDM type in both 'new' and 'old'.")
        return values


# copy of Message and BaseMessage from models.message
class LdapMessage(BaseModel):
    """Must be compatible with both pydantic v1 and v2"""

    publisher_name: PublisherName = Field(description="The name of the publisher of the message.")
    ts: datetime = Field(description="The timestamp when the message was received by the dispatcher.")

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: Body = Field(description="The content of the message as a key/value dictionary.")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


def messagepack_encoder(data: Any) -> bytes:
    return msgpack.packb(data, default=pydantic_encoder)


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    @staticmethod
    def stream(subject: str) -> str:
        return f"stream:{subject}"

    @staticmethod
    def durable_name(subject: str) -> str:
        return f"durable_name:{subject}"


# copy of NatsMessageQueue from backends.nats_mq
class NatsMessageQueue:
    """
    Message queueing using NATS.

    Use as an asynchronous context manager to ensure the connection gets closed after usage.
    """

    def __init__(self, server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs):
        self._server = server
        self._user = user
        self._password = password
        self._max_reconnect_attempts = max_reconnect_attempts
        self._connect_kwargs = connect_kwargs
        self._nats = NATS()
        self._js = self._nats.jetstream()

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self):
        """
        Connect to the NATS server.

        Arguments are passed directly to the NATS client.
        https://nats-io.github.io/nats.py/modules.html#asyncio-client

        By default, it fails after a maximum of 10 seconds because of a 2 second connect timout * 5 reconnect attempts.
        """
        await self._nats.connect(
            servers=self._server,
            user=self._user,
            password=self._password,
            max_reconnect_attempts=self._max_reconnect_attempts,
            error_cb=self.error_callback,
            disconnected_cb=self.disconnected_callback,
            closed_cb=self.closed_callback,
            reconnected_cb=self.reconnected_callback,
            **self._connect_kwargs,
        )

    async def error_callback(self, e):
        logger.error("There was an error during the execution: %s", e)

    async def disconnected_callback(self):
        logger.debug("Disconnected to NATS")

    async def closed_callback(self):
        logger.debug("Closed connection to NATS.")

    async def reconnected_callback(self):
        logger.debug("Reconnected to NATS")

    async def close(self):
        await self._nats.close()

    async def add_message(
        self,
        stream: str,
        subject: str,
        message: LdapMessage,
        binary_encoder: Callable[[Any], bytes] = messagepack_encoder,
    ):
        """Publish a message to a NATS subject."""
        stream_name = NatsKeys.stream(stream)

        await self._js.publish(
            subject,
            binary_encoder(message.dict()),
            stream=stream_name,
        )
        logger.debug(
            "Message was published to the stream: %r with the subject: %r",
            stream_name,
            subject,
        )

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: Optional[list[str]] = None):
        stream_name = NatsKeys.stream(stream)
        stream_config = StreamConfig(
            name=stream_name,
            subjects=subjects or [stream],
            retention=RetentionPolicy.LIMITS if manual_delete else RetentionPolicy.WORK_QUEUE,
            # TODO: set to 3 after nats clustering is stable.
            num_replicas=1,
        )
        try:
            await self._js.stream_info(stream_name)
            logger.info("A stream with the name %r already exists", stream_name)
        except NotFoundError:
            await self._js.add_stream(stream_config)
            logger.info("A stream with the name %r was created", stream_name)
        else:
            await self._js.update_stream(stream_config)
            logger.info("A stream with the name %r was updated", stream_name)


class MessageQueueNatsAdapter(MessageQueuePort):
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        super().__init__(settings or ldap_producer_settings())
        self.mq: Optional[NatsMessageQueue] = None

    async def __aenter__(self):
        self.mq = NatsMessageQueue(
            self.settings.nats_server,
            self.settings.nats_user,
            self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        await self.mq.connect()
        return self

    async def __aexit__(self, *args):
        await self.mq.close()
        self.mq = None
        return False

    async def enqueue_change_event(self, new: Dict[str, Any], old: Dict[str, Any]) -> None:
        message = LdapMessage(
            publisher_name=PublisherName.ldif_producer,
            ts=datetime.now(),
            realm="ldap",
            topic="ldap",
            body=Body(new=new, old=old),
        )
        await self.mq.add_message(LDAP_PRODUCER_QUEUE_NAME, LDAP_SUBJECT, message, binary_encoder=messagepack_encoder)

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LDAP_PRODUCER_QUEUE_NAME, False, [LDAP_SUBJECT])
