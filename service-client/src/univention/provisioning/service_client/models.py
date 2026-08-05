# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Validated values used to describe a Provisioning subscription."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any


class DefinitionError(ValueError):
    """The supplied subscription definition is invalid."""


_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_REALM_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_TOPIC_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,254}\Z")
_TOP_LEVEL_KEYS = frozenset({"name", "realms_topics", "request_prefill", "password", "password_file"})
_REQUIRED_TOP_LEVEL_KEYS = frozenset({"name", "realms_topics", "request_prefill"})
_REALM_TOPIC_KEYS = frozenset({"realm", "topic"})


def _validate_safe_string(value: Any, *, field: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise DefinitionError(f"{field} must be a non-empty safe string")
    return value


@dataclass(frozen=True, slots=True)
class RealmTopic:
    """One exact realm/topic pair consumed by the subscription."""

    realm: str
    topic: str

    def __post_init__(self) -> None:
        _validate_safe_string(self.realm, field="realm", pattern=_REALM_PATTERN)
        _validate_safe_string(self.topic, field="topic", pattern=_TOPIC_PATTERN)

    @classmethod
    def from_mapping(cls, value: object) -> RealmTopic:
        if not isinstance(value, Mapping):
            raise DefinitionError("each realms_topics entry must be an object")
        keys = set(value)
        if keys != _REALM_TOPIC_KEYS:
            raise DefinitionError("each realms_topics entry must contain exactly realm and topic")
        return cls(realm=value["realm"], topic=value["topic"])

    def to_dict(self) -> dict[str, str]:
        """Return the stable JSON representation expected by the API."""

        return {"realm": self.realm, "topic": self.topic}


@dataclass(frozen=True, slots=True)
class SubscriptionDefinition:
    """The complete non-secret definition of a Provisioning subscription."""

    name: str
    realms_topics: tuple[RealmTopic, ...]
    request_prefill: bool

    def __post_init__(self) -> None:
        _validate_safe_string(self.name, field="name", pattern=_NAME_PATTERN)
        if not isinstance(self.realms_topics, tuple) or not self.realms_topics:
            raise DefinitionError("realms_topics must be a non-empty array")
        if any(not isinstance(item, RealmTopic) for item in self.realms_topics):
            raise DefinitionError("realms_topics must contain only realm/topic objects")
        if len(set(self.realms_topics)) != len(self.realms_topics):
            raise DefinitionError("realms_topics must not contain duplicate entries")
        if not isinstance(self.request_prefill, bool):
            raise DefinitionError("request_prefill must be a boolean")

    @classmethod
    def from_json(cls, value: str) -> SubscriptionDefinition:
        """Parse one complete definition from a JSON command-line value."""

        if not isinstance(value, str):
            raise DefinitionError("subscription definition must be JSON text")
        try:
            decoded = json.loads(value)
        except (json.JSONDecodeError, RecursionError) as exc:
            raise DefinitionError("subscription definition is not valid JSON") from exc
        return cls.from_mapping(decoded)

    @classmethod
    def from_mapping(cls, value: object) -> SubscriptionDefinition:
        """Validate a decoded JSON object.

        ``password`` and ``password_file`` are accepted for compatibility but
        deliberately ignored. Secret handling belongs to the client.
        """

        if not isinstance(value, Mapping):
            raise DefinitionError("subscription definition must be a JSON object")

        keys = set(value)
        unknown = keys - _TOP_LEVEL_KEYS
        missing = _REQUIRED_TOP_LEVEL_KEYS - keys
        if unknown:
            raise DefinitionError(f"subscription definition contains unknown fields: {', '.join(sorted(unknown))}")
        if missing:
            raise DefinitionError(f"subscription definition is missing fields: {', '.join(sorted(missing))}")

        raw_topics = value["realms_topics"]
        if not isinstance(raw_topics, list) or not raw_topics:
            raise DefinitionError("realms_topics must be a non-empty array")

        return cls(
            name=_validate_safe_string(value["name"], field="name", pattern=_NAME_PATTERN),
            realms_topics=tuple(RealmTopic.from_mapping(item) for item in raw_topics),
            request_prefill=value["request_prefill"],
        )

    def with_request_prefill(self, request_prefill: bool) -> SubscriptionDefinition:
        """Return a copy with the requested prefill behavior."""

        if not isinstance(request_prefill, bool):
            raise DefinitionError("request_prefill must be a boolean")
        return replace(self, request_prefill=request_prefill)

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic, JSON-compatible API definition."""

        return {
            "name": self.name,
            "realms_topics": [item.to_dict() for item in self.realms_topics],
            "request_prefill": self.request_prefill,
        }
