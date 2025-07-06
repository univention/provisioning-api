# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import Any

import msgpack
from pydantic import BaseModel, Field, root_validator
from pydantic.json import pydantic_encoder

from .constants import PublisherName

logger = logging.getLogger(__name__)


class EmptyBodyError(Exception): ...


class LdapBody(BaseModel):
    old: dict[str, Any] = Field(description="The LDAP/UDM object before the change.")
    new: dict[str, Any] = Field(description="The LDAP/UDM object after the change.")

    @root_validator(pre=True)
    def check_not_both_empty(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not values.get("old") and not values.get("new"):
            raise EmptyBodyError("'old' and 'new' cannot be both empty.")
        return values


class LdapMessage(BaseModel):
    """Must be compatible with both pydantic v1 and v2"""

    publisher_name: PublisherName = Field(description="The name of the publisher of the message.")
    ts: datetime = Field(description="The timestamp when the message was received by the dispatcher.")

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: LdapBody = Field(description="The content of the message as a key/value dictionary.")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }

    def binary_dump(self) -> bytes:
        return msgpack.packb(self.dict(), default=pydantic_encoder)
