# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Client-side lifecycle management for Provisioning subscriptions."""

from .api import (
    APIAuthenticationError,
    APIConflictError,
    APIConnectionError,
    APIError,
    APINotFoundError,
    APIResponseError,
    APIUnavailableError,
    ProvisioningAPI,
)
from .manager import (
    LifecycleError,
    SubscriptionCollisionError,
    SubscriptionManager,
    SubscriptionOutcome,
)
from .models import DefinitionError, SubscriptionDefinition
from .storage import StorageError, SubscriptionRecord, SubscriptionStore

__version__ = "0.1.0"

__all__ = [
    "APIAuthenticationError",
    "APIConflictError",
    "APIConnectionError",
    "APIError",
    "APINotFoundError",
    "APIResponseError",
    "APIUnavailableError",
    "DefinitionError",
    "LifecycleError",
    "ProvisioningAPI",
    "StorageError",
    "SubscriptionCollisionError",
    "SubscriptionDefinition",
    "SubscriptionManager",
    "SubscriptionOutcome",
    "SubscriptionRecord",
    "SubscriptionStore",
]
