# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any

from pydantic import BaseModel


class MQMessage(BaseModel):
    subject: str
    reply: str
    data: dict[str, Any]
    num_delivered: int
    sequence_number: int
    headers: dict[str, str] | None = None
