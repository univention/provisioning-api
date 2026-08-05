# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Crash-safe lifecycle management for one Provisioning subscription."""

from __future__ import annotations

import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any, Literal

from .api import APIAuthenticationError, APINotFoundError, ProvisioningAPI
from .models import DefinitionError, SubscriptionDefinition
from .storage import SubscriptionRecord, SubscriptionStore

ADMIN_USERNAME = "admin"


class LifecycleError(RuntimeError):
    """A subscription could not be changed without risking its credentials or queue."""


class SubscriptionCollisionError(LifecycleError):
    """The requested name exists but the managed subscriber password is unavailable."""


@dataclass(frozen=True, slots=True)
class SubscriptionOutcome:
    """Non-secret summary of a completed lifecycle action."""

    name: str
    action: Literal["created", "reused", "recovered", "replaced", "removed", "already-absent"]
    queue_replaced: bool = False


class SubscriptionManager:
    """Create, recover, validate, and remove one managed subscription."""

    def __init__(
        self,
        api: ProvisioningAPI,
        store: SubscriptionStore,
        admin_password_provider: Callable[[], str],
        *,
        password_factory: Callable[[], str] | None = None,
    ) -> None:
        self.api = api
        self.store = store
        self._admin_password_provider = admin_password_provider
        self._password_factory = password_factory or (lambda: secrets.token_urlsafe(32))

    def subscribe(
        self,
        definition: SubscriptionDefinition,
        *,
        generate_password: bool,
        force: bool = False,
    ) -> SubscriptionOutcome:
        """Ensure that the requested subscription exists and can be authenticated.

        The limited subscriber password is staged before the administrative API
        request. A retry therefore uses the exact same password even if the first
        API response was lost after the server created the subscription.
        """

        if not isinstance(definition, SubscriptionDefinition):
            raise TypeError("definition must be a SubscriptionDefinition")

        record = self.store.load()
        if record is None:
            if not generate_password:
                raise LifecycleError("No managed subscription exists; --generate-password is required.")
            record = SubscriptionRecord.candidate(
                base_url=self.api.base_url,
                definition=definition,
                password=self._password_factory(),
                replacement_authorized=force,
            )
            self.store.save(record)
            return self._create_candidate(record)

        self._ensure_compatible_input(record, definition)
        if record.state == "candidate" and force and not record.replacement_authorized:
            record = record.authorize_replacement()
            self.store.save(record)
        return self._reuse_or_repair(record, force=force)

    def unsubscribe(self) -> SubscriptionOutcome:
        """Remove a subscription with its own limited credentials.

        The local file is retained on network or server errors so that cleanup
        can be retried without losing the only plaintext copy of the subscriber
        password. If limited authentication is rejected, the administrator
        credential is fetched lazily only to confirm that the exact subscription
        is already absent after a possibly lost successful DELETE response.
        """

        record = self.store.load()
        if record is None:
            return SubscriptionOutcome(name="", action="already-absent")

        try:
            self.api.delete_subscription(record.name, record.password)
        except APINotFoundError:
            pass
        except APIAuthenticationError:
            admin_password = self._admin_password()
            if self._subscription_is_listed(record.name, admin_password):
                raise LifecycleError(
                    "The Provisioning subscription still exists, but its limited password was rejected; "
                    "the local credential was retained."
                ) from None
        self.store.delete()
        return SubscriptionOutcome(name=record.name, action="removed")

    def _create_candidate(self, record: SubscriptionRecord) -> SubscriptionOutcome:
        admin_password = self._admin_password()
        collision = self._subscription_is_listed(record.name, admin_password)
        replaced = False
        if collision:
            if not record.replacement_authorized:
                raise SubscriptionCollisionError(
                    "A Provisioning subscription with this exact name already exists, but no usable managed "
                    "password is available. Retry with --force only if discarding its pending queue is acceptable."
                )
            self._admin_delete(record.name, admin_password)
            replaced = True

        self.api.create_subscription(record.definition.to_dict(), record.password, ADMIN_USERNAME, admin_password)
        self._validate_remote(record, compare_prefill=True)
        self.store.save(record.activate())
        return SubscriptionOutcome(
            name=record.name,
            action="replaced" if replaced else "created",
            queue_replaced=replaced,
        )

    def _reuse_or_repair(self, record: SubscriptionRecord, *, force: bool) -> SubscriptionOutcome:
        try:
            remote = self.api.get_subscription(record.name, record.password)
        except (APIAuthenticationError, APINotFoundError):
            return self._repair(record, force=force)

        self._assert_remote_matches(remote, record.definition, compare_prefill=record.state == "candidate")
        active = replace(record.activate(), base_url=self.api.base_url)
        if active != record:
            self.store.save(active)
        return SubscriptionOutcome(name=record.name, action="reused")

    def _repair(self, record: SubscriptionRecord, *, force: bool) -> SubscriptionOutcome:
        original_state = record.state
        if force and not record.replacement_authorized:
            record = SubscriptionRecord.candidate(
                base_url=self.api.base_url,
                definition=record.definition,
                password=record.password,
                replacement_authorized=True,
            )
            self.store.save(record)

        admin_password = self._admin_password()
        collision = self._subscription_is_listed(record.name, admin_password)
        if collision and not record.replacement_authorized:
            raise SubscriptionCollisionError(
                "The managed subscriber password was rejected, but a subscription with this exact name exists. "
                "It was not replaced because deletion would discard pending events."
            )
        if collision:
            self._admin_delete(record.name, admin_password)

        definition = record.definition
        if original_state == "active" and not collision:
            # Recreating a subscription that disappeared is a recovery. Ask for
            # the current directory state even when the original migration did
            # not request a prefill.
            definition = definition.with_request_prefill(True)
        candidate = SubscriptionRecord.candidate(
            base_url=self.api.base_url,
            definition=definition,
            password=record.password,
            replacement_authorized=record.replacement_authorized,
        )
        self.store.save(candidate)
        self.api.create_subscription(definition.to_dict(), candidate.password, ADMIN_USERNAME, admin_password)
        self._validate_remote(candidate, compare_prefill=True)
        self.store.save(candidate.activate())
        if collision:
            action = "replaced"
        elif original_state == "candidate":
            action = "created"
        else:
            action = "recovered"
        return SubscriptionOutcome(
            name=candidate.name,
            action=action,
            queue_replaced=collision,
        )

    def _admin_password(self) -> str:
        password = self._admin_password_provider()
        if not isinstance(password, str) or not password:
            raise LifecycleError("The Provisioning administrator password is unavailable.")
        return password

    def _subscription_is_listed(self, name: str, admin_password: str) -> bool:
        subscriptions = self.api.list_subscriptions(ADMIN_USERNAME, admin_password)
        return any(item.get("name") == name for item in subscriptions)

    def _admin_delete(self, name: str, admin_password: str) -> None:
        try:
            self.api.admin_delete_subscription(name, ADMIN_USERNAME, admin_password)
        except APINotFoundError:
            # The exact subscription disappeared between list and delete. The
            # subsequent idempotent create is still safe.
            pass

    def _validate_remote(self, record: SubscriptionRecord, *, compare_prefill: bool) -> None:
        remote = self.api.get_subscription(record.name, record.password)
        self._assert_remote_matches(remote, record.definition, compare_prefill=compare_prefill)

    @staticmethod
    def _assert_remote_matches(
        remote: Mapping[str, Any],
        expected: SubscriptionDefinition,
        *,
        compare_prefill: bool,
    ) -> None:
        try:
            actual = SubscriptionDefinition.from_mapping(
                {
                    "name": remote["name"],
                    "realms_topics": remote["realms_topics"],
                    "request_prefill": remote["request_prefill"],
                }
            )
        except (KeyError, DefinitionError, TypeError) as exc:
            raise LifecycleError("The Provisioning API returned an invalid subscription definition.") from exc

        matches = actual.name == expected.name and actual.realms_topics == expected.realms_topics
        if compare_prefill:
            matches = matches and actual.request_prefill == expected.request_prefill
        if not matches:
            raise LifecycleError(
                "The remote Provisioning subscription does not match the managed definition; it was not changed."
            )

    @staticmethod
    def _ensure_compatible_input(record: SubscriptionRecord, requested: SubscriptionDefinition) -> None:
        # Once a credential file exists its name is authoritative, even after a
        # hostname change. Topics may never change silently because replacing a
        # subscription can discard queued events.
        if record.definition.realms_topics != requested.realms_topics:
            raise LifecycleError(
                "The requested topics differ from the managed subscription; explicit migration is required."
            )
