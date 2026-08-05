# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from univention.provisioning import service_client


def test_supported_python_api_is_exported():
    expected = {
        "ProvisioningAPI",
        "SubscriptionDefinition",
        "SubscriptionManager",
        "SubscriptionRecord",
        "SubscriptionStore",
    }

    assert expected <= set(service_client.__all__)
    assert all(getattr(service_client, name) is not None for name in expected)
