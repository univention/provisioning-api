# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import json

import pytest

from univention.provisioning.service_client.models import DefinitionError, RealmTopic, SubscriptionDefinition


def definition_json(**changes: object) -> str:
    value: dict[str, object] = {
        "name": "ox-connector-ucs-3220",
        "realms_topics": [
            {"realm": "oxmail", "topic": "oxcontext"},
            {"realm": "users", "topic": "user"},
        ],
        "request_prefill": True,
    }
    value.update(changes)
    return json.dumps(value)


def test_parse_complete_definition_and_emit_stable_api_mapping() -> None:
    definition = SubscriptionDefinition.from_json(definition_json())

    assert definition == SubscriptionDefinition(
        name="ox-connector-ucs-3220",
        realms_topics=(
            RealmTopic(realm="oxmail", topic="oxcontext"),
            RealmTopic(realm="users", topic="user"),
        ),
        request_prefill=True,
    )
    assert definition.to_dict() == {
        "name": "ox-connector-ucs-3220",
        "realms_topics": [
            {"realm": "oxmail", "topic": "oxcontext"},
            {"realm": "users", "topic": "user"},
        ],
        "request_prefill": True,
    }


def test_input_password_fields_are_accepted_but_ignored() -> None:
    definition = SubscriptionDefinition.from_json(
        definition_json(password="must-not-be-used", password_file="/tmp/must-not-be-read")
    )

    assert definition.to_dict() == {
        "name": "ox-connector-ucs-3220",
        "realms_topics": [
            {"realm": "oxmail", "topic": "oxcontext"},
            {"realm": "users", "topic": "user"},
        ],
        "request_prefill": True,
    }
    assert not hasattr(definition, "password")
    assert "must-not-be-used" not in repr(definition)


@pytest.mark.parametrize(
    "raw",
    [
        "not JSON",
        "[]",
        "null",
        definition_json(unexpected="field"),
        json.dumps({"name": "only-a-name"}),
        definition_json(name=""),
        definition_json(name="bad name"),
        definition_json(name="../unsafe"),
        definition_json(realms_topics=[]),
        definition_json(realms_topics="users/user"),
        definition_json(realms_topics=[{"realm": "users"}]),
        definition_json(realms_topics=[{"realm": "users", "topic": "user", "extra": True}]),
        definition_json(realms_topics=[{"realm": "users", "topic": "bad topic"}]),
        definition_json(realms_topics=[{"realm": "", "topic": "user"}]),
        definition_json(request_prefill=1),
    ],
)
def test_malformed_definition_is_rejected(raw: str) -> None:
    with pytest.raises(DefinitionError):
        SubscriptionDefinition.from_json(raw)


def test_duplicate_realm_topic_is_rejected() -> None:
    topic = {"realm": "users", "topic": "user"}

    with pytest.raises(DefinitionError, match="duplicate"):
        SubscriptionDefinition.from_json(definition_json(realms_topics=[topic, topic]))


def test_models_are_immutable() -> None:
    definition = SubscriptionDefinition.from_json(definition_json())

    with pytest.raises(AttributeError):
        definition.name = "changed"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        definition.realms_topics[0].realm = "changed"  # type: ignore[misc]


def test_request_prefill_override_returns_a_new_validated_definition() -> None:
    original = SubscriptionDefinition.from_json(definition_json())

    changed = original.with_request_prefill(False)

    assert original.request_prefill is True
    assert changed.request_prefill is False
    assert changed.name == original.name
    assert changed.realms_topics == original.realms_topics


def test_from_json_only_accepts_text() -> None:
    with pytest.raises(DefinitionError, match="JSON text"):
        SubscriptionDefinition.from_json(b"{}")  # type: ignore[arg-type]
