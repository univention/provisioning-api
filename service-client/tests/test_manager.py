# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from univention.provisioning.service_client.api import (
    APIAuthenticationError,
    APIConnectionError,
    APINotFoundError,
)
from univention.provisioning.service_client.manager import (
    LifecycleError,
    SubscriptionCollisionError,
    SubscriptionManager,
)
from univention.provisioning.service_client.models import SubscriptionDefinition
from univention.provisioning.service_client.storage import SubscriptionRecord, SubscriptionStore

BASE_URL = "https://primary.example.test/univention/provisioning"
PASSWORD = "limited-subscriber-secret"
ADMIN_PASSWORD = "powerful-admin-secret"


def definition(*, name: str = "ox-connector-member", prefill: bool = False, topic: str = "users/user"):
    return SubscriptionDefinition.from_mapping(
        {
            "name": name,
            "realms_topics": [{"realm": "udm", "topic": topic}],
            "request_prefill": prefill,
        }
    )


def remote_value(value: SubscriptionDefinition) -> dict[str, object]:
    return {**value.to_dict(), "prefill_queue_status": "done"}


class FakeAPI:
    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.remote: dict[str, dict[str, object]] = {}
        self.passwords: dict[str, str] = {}
        self.calls: list[tuple[object, ...]] = []
        self.create_error: Exception | None = None
        self.list_error: Exception | None = None
        self.admin_delete_error: Exception | None = None

    def get_subscription(self, name: str, password: str) -> dict[str, object]:
        self.calls.append(("get", name, password))
        if name not in self.remote:
            raise APIAuthenticationError()
        if self.passwords[name] != password:
            raise APIAuthenticationError()
        return self.remote[name]

    def list_subscriptions(self, username: str, password: str) -> list[dict[str, object]]:
        self.calls.append(("list", username, password))
        if self.list_error is not None:
            raise self.list_error
        return list(self.remote.values())

    def create_subscription(self, value, password: str, username: str, admin_password: str) -> bool:
        self.calls.append(("create", value, password, username, admin_password))
        if self.create_error is not None:
            raise self.create_error
        subscription = SubscriptionDefinition.from_mapping(value)
        self.remote[subscription.name] = remote_value(subscription)
        self.passwords[subscription.name] = password
        return True

    def delete_subscription(self, name: str, password: str) -> None:
        self.calls.append(("delete", name, password))
        if name not in self.remote:
            # The real API authenticates before looking up the subscription.
            raise APIAuthenticationError()
        if self.passwords[name] != password:
            raise APIAuthenticationError()
        del self.remote[name]
        del self.passwords[name]

    def admin_delete_subscription(self, name: str, username: str, password: str) -> None:
        self.calls.append(("admin-delete", name, username, password))
        if self.admin_delete_error is not None:
            raise self.admin_delete_error
        if name not in self.remote:
            raise APINotFoundError()
        del self.remote[name]
        del self.passwords[name]


@pytest.fixture
def store(tmp_path) -> SubscriptionStore:
    directory = tmp_path / "runtime-secrets"
    return SubscriptionStore(directory / "subscription.json")


def manager(
    api: FakeAPI,
    store: SubscriptionStore,
    provider: Callable[[], str] = lambda: ADMIN_PASSWORD,
) -> SubscriptionManager:
    return SubscriptionManager(api, store, provider, password_factory=lambda: PASSWORD)  # type: ignore[arg-type]


def save(store: SubscriptionStore, value: SubscriptionDefinition, *, state: str = "active") -> SubscriptionRecord:
    candidate = SubscriptionRecord.candidate(base_url=BASE_URL, definition=value, password=PASSWORD)
    record = candidate.activate() if state == "active" else candidate
    store.save(record)
    return record


def install_remote(api: FakeAPI, value: SubscriptionDefinition, password: str = PASSWORD) -> None:
    api.remote[value.name] = remote_value(value)
    api.passwords[value.name] = password


def test_fresh_subscribe_stages_password_before_fetching_admin_credentials(store):
    api = FakeAPI()

    def provider() -> str:
        staged = store.load()
        assert staged is not None
        assert staged.state == "candidate"
        assert staged.password == PASSWORD
        return ADMIN_PASSWORD

    outcome = manager(api, store, provider).subscribe(definition(prefill=True), generate_password=True)

    assert outcome.action == "created"
    assert store.load().state == "active"  # type: ignore[union-attr]


def test_fresh_subscribe_requires_explicit_password_generation(store):
    api = FakeAPI()

    with pytest.raises(LifecycleError, match="generate-password"):
        manager(api, store).subscribe(definition(), generate_password=False)

    assert store.load() is None
    assert api.calls == []


def test_fresh_collision_is_not_replaced_without_force(store):
    api = FakeAPI()
    value = definition()
    install_remote(api, value, "unknown-old-secret")

    with pytest.raises(SubscriptionCollisionError, match="pending queue"):
        manager(api, store).subscribe(value, generate_password=True)

    assert store.load().state == "candidate"  # type: ignore[union-attr]
    assert not any(call[0] == "admin-delete" for call in api.calls)


def test_force_replaces_exact_collision_and_reports_queue_loss(store):
    api = FakeAPI()
    value = definition(prefill=True)
    install_remote(api, value, "unknown-old-secret")

    outcome = manager(api, store).subscribe(value, generate_password=True, force=True)

    assert outcome.action == "replaced"
    assert outcome.queue_replaced is True
    assert api.passwords[value.name] == PASSWORD
    assert store.load().replacement_authorized is False  # type: ignore[union-attr]


def test_candidate_retry_promotes_successful_prior_creation_without_admin(store):
    api = FakeAPI()
    value = definition(prefill=True)
    save(store, value, state="candidate")
    install_remote(api, value)

    def unexpected_provider() -> str:
        raise AssertionError("admin credentials must not be fetched")

    outcome = manager(api, store, unexpected_provider).subscribe(value, generate_password=True)

    assert outcome.action == "reused"
    assert store.load().state == "active"  # type: ignore[union-attr]


def test_candidate_retry_creates_when_first_attempt_failed_before_api_creation(store):
    api = FakeAPI()
    value = definition(prefill=True)
    save(store, value, state="candidate")

    outcome = manager(api, store).subscribe(value, generate_password=True)

    assert outcome.action == "created"
    assert store.load().state == "active"  # type: ignore[union-attr]


def test_active_subscription_is_reused_without_admin_access(store):
    api = FakeAPI()
    value = definition(prefill=True)
    save(store, value)
    install_remote(api, value)

    def unexpected_provider() -> str:
        raise AssertionError("admin credentials must not be fetched")

    outcome = manager(api, store, unexpected_provider).subscribe(
        definition(prefill=False),
        generate_password=True,
    )

    assert outcome.action == "reused"
    assert [call[0] for call in api.calls] == ["get"]


def test_stored_name_remains_authoritative_after_hostname_change(store):
    api = FakeAPI()
    stored = definition(name="ox-connector-old-host")
    save(store, stored)
    install_remote(api, stored)

    outcome = manager(api, store).subscribe(
        definition(name="ox-connector-new-host"),
        generate_password=True,
    )

    assert outcome.name == stored.name
    assert ("get", stored.name, PASSWORD) in api.calls


def test_topic_change_aborts_before_remote_operation(store):
    api = FakeAPI()
    save(store, definition())

    with pytest.raises(LifecycleError, match="topics differ"):
        manager(api, store).subscribe(definition(topic="groups/group"), generate_password=True)

    assert api.calls == []


def test_missing_active_subscription_is_recovered_with_same_password_and_prefill(store):
    api = FakeAPI()
    value = definition(prefill=False)
    save(store, value)

    outcome = manager(api, store).subscribe(value, generate_password=True)

    active = store.load()
    assert outcome.action == "recovered"
    assert active is not None
    assert active.password == PASSWORD
    assert active.definition.request_prefill is True
    assert api.passwords[value.name] == PASSWORD


def test_rejected_local_password_does_not_replace_existing_subscription(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    install_remote(api, value, "different-secret")

    with pytest.raises(SubscriptionCollisionError, match="not replaced"):
        manager(api, store).subscribe(value, generate_password=True)

    assert api.passwords[value.name] == "different-secret"
    assert store.load().state == "active"  # type: ignore[union-attr]


def test_explicit_force_can_recover_rejected_local_password(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    install_remote(api, value, "different-secret")

    outcome = manager(api, store).subscribe(value, generate_password=True, force=True)

    assert outcome.action == "replaced"
    assert outcome.queue_replaced is True
    assert api.passwords[value.name] == PASSWORD


def test_failed_create_leaves_candidate_for_idempotent_retry(store):
    api = FakeAPI()
    api.create_error = APIConnectionError()

    with pytest.raises(APIConnectionError):
        manager(api, store).subscribe(definition(), generate_password=True)

    candidate = store.load()
    assert candidate is not None
    assert candidate.state == "candidate"
    assert candidate.password == PASSWORD


def test_failed_admin_delete_retains_force_authorization_for_retry(store):
    api = FakeAPI()
    value = definition(prefill=True)
    install_remote(api, value, "unknown-old-secret")
    api.admin_delete_error = APIConnectionError()

    with pytest.raises(APIConnectionError):
        manager(api, store).subscribe(value, generate_password=True, force=True)

    candidate = store.load()
    assert candidate is not None
    assert candidate.state == "candidate"
    assert candidate.replacement_authorized is True
    assert api.passwords[value.name] == "unknown-old-secret"

    api.admin_delete_error = None
    outcome = manager(api, store).subscribe(value, generate_password=True)

    assert outcome.action == "replaced"
    assert outcome.queue_replaced is True
    active = store.load()
    assert active is not None
    assert active.state == "active"
    assert active.replacement_authorized is False
    assert api.passwords[value.name] == PASSWORD


def test_failed_create_retains_force_authorization_until_retry_activates(store):
    api = FakeAPI()
    value = definition(prefill=True)
    install_remote(api, value, "unknown-old-secret")
    api.create_error = APIConnectionError()

    with pytest.raises(APIConnectionError):
        manager(api, store).subscribe(value, generate_password=True, force=True)

    candidate = store.load()
    assert candidate is not None
    assert candidate.state == "candidate"
    assert candidate.replacement_authorized is True
    assert value.name not in api.remote

    api.create_error = None
    manager(api, store).subscribe(value, generate_password=True)

    active = store.load()
    assert active is not None
    assert active.state == "active"
    assert active.replacement_authorized is False
    assert api.passwords[value.name] == PASSWORD


def test_active_record_never_inherits_prior_force_authorization(store):
    api = FakeAPI()
    value = definition()
    active = SubscriptionRecord.candidate(
        base_url=BASE_URL,
        definition=value,
        password=PASSWORD,
        replacement_authorized=True,
    ).activate()
    store.save(active)
    install_remote(api, value, "different-secret")

    with pytest.raises(SubscriptionCollisionError, match="not replaced"):
        manager(api, store).subscribe(value, generate_password=True)

    assert store.load() == active
    assert active.replacement_authorized is False
    assert api.passwords[value.name] == "different-secret"
    assert not any(call[0] == "admin-delete" for call in api.calls)


def test_remote_definition_mismatch_is_not_changed(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    install_remote(api, definition(topic="groups/group"))
    api.remote[value.name] = remote_value(definition(name=value.name, topic="groups/group"))
    api.passwords[value.name] = PASSWORD

    with pytest.raises(LifecycleError, match="does not match"):
        manager(api, store).subscribe(value, generate_password=True)

    assert not any(call[0] in ("create", "admin-delete") for call in api.calls)


def test_unsubscribe_uses_limited_credentials_then_removes_file(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    install_remote(api, value)

    provider = Mock(side_effect=AssertionError("admin credentials must stay lazy on successful DELETE"))
    outcome = manager(api, store, provider).unsubscribe()

    assert outcome.action == "removed"
    assert api.calls == [("delete", value.name, PASSWORD)]
    provider.assert_not_called()
    assert store.load() is None


def test_unsubscribe_rejects_different_api_endpoint_before_remote_operation(store):
    api = FakeAPI()
    api.base_url = "https://backup.example.test/univention/provisioning"
    value = definition()
    record = save(store, value)
    install_remote(api, value)
    provider = Mock(return_value=ADMIN_PASSWORD)

    with pytest.raises(LifecycleError, match="does not match the endpoint stored"):
        manager(api, store, provider).unsubscribe()

    assert api.calls == []
    provider.assert_not_called()
    assert store.load() == record


def test_unsubscribe_accepts_equivalent_stored_endpoint_spelling(store):
    api = FakeAPI()
    value = definition()
    record = SubscriptionRecord.candidate(
        base_url="https://PRIMARY.EXAMPLE.TEST:443/univention/provisioning/",
        definition=value,
        password=PASSWORD,
    ).activate()
    store.save(record)
    install_remote(api, value)

    outcome = manager(api, store).unsubscribe()

    assert outcome.action == "removed"
    assert store.load() is None


def test_unsubscribe_treats_missing_remote_subscription_as_success(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    provider = Mock(return_value=ADMIN_PASSWORD)

    outcome = manager(api, store, provider).unsubscribe()

    assert outcome.action == "removed"
    assert api.calls == [
        ("delete", value.name, PASSWORD),
        ("list", "admin", ADMIN_PASSWORD),
    ]
    provider.assert_called_once_with()
    assert store.load() is None


def test_unsubscribe_failure_retains_only_local_password_copy(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    install_remote(api, value, "different-secret")

    provider = Mock(return_value=ADMIN_PASSWORD)
    with pytest.raises(LifecycleError, match="still exists"):
        manager(api, store, provider).unsubscribe()

    provider.assert_called_once_with()
    assert store.load() is not None


def test_unsubscribe_confirmation_failure_retains_local_password_copy(store):
    api = FakeAPI()
    value = definition()
    save(store, value)
    api.list_error = APIConnectionError()
    provider = Mock(return_value=ADMIN_PASSWORD)

    with pytest.raises(APIConnectionError):
        manager(api, store, provider).unsubscribe()

    provider.assert_called_once_with()
    assert store.load() is not None


def test_unsubscribe_without_file_is_idempotent(store):
    api = FakeAPI()

    outcome = manager(api, store).unsubscribe()

    assert outcome.action == "already-absent"
    assert api.calls == []
