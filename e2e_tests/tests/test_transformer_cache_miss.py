# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import uuid

import pytest

from univention.admin.rest.client import UDM
from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.constants import BucketName
from univention.provisioning.models.message import MessageProcessingStatus
from univention.provisioning.models.subscription import RealmTopic

from .mock_data import GROUPS_TOPIC, REALM


@pytest.fixture
async def nats_kv_manager(nats_connection):
    js = nats_connection.jetstream()
    kv = await js.key_value(bucket=BucketName.cache.value)
    yield kv


@pytest.fixture
async def groups_subscription(create_subscription):
    return await create_subscription([RealmTopic(realm=REALM, topic=GROUPS_TOPIC)])


async def test_cache_miss_during_modification(
    groups_subscription: str,
    provisioning_client: ProvisioningConsumerClient,
    nats_kv_manager,
    udm: UDM,
    ldap_base: str,
):
    """
    Test that when the cache is empty (cache miss), the transformer
    reconstructs the old object from LDAP.

    Scenario:
    1. Create a group
    2. Consume the creation message (populates cache)
    3. Delete cache entry (simulate cache miss)
    4. Modify the group
    5. Verify modification event has both old and new objects
    """
    group_name = f"test-cache-miss-{uuid.uuid4()}"
    group_dn = f"cn={group_name},cn=groups,{ldap_base}"

    group_mod = udm.get(GROUPS_TOPIC)
    group = group_mod.new()
    group.properties.update({"name": group_name, "description": "original description"})
    group.save()
    print(f"Created group {group.dn!r}.")

    create_message = await provisioning_client.get_subscription_message(
        name=groups_subscription,
        timeout=5,
    )
    assert create_message is not None
    assert create_message.body.new["dn"] == group_dn

    group_uuid = create_message.body.new["uuid"]

    await provisioning_client.set_message_status(
        groups_subscription, create_message.sequence_number, MessageProcessingStatus.ok
    )

    await nats_kv_manager.delete(group_uuid)
    print(f"Deleted cache entry for UUID {group_uuid}")

    group.reload()
    group.properties["description"] = "modified description after cache deletion"
    group.save()
    print(f"Modified group {group.dn!r}.")

    modify_message = await provisioning_client.get_subscription_message(
        name=groups_subscription,
        timeout=10,
    )
    assert modify_message is not None, "Modification message should arrive despite cache miss"

    old_obj = modify_message.body.old
    new_obj = modify_message.body.new

    assert old_obj and new_obj, "Both old and new objects should be present despite cache miss"
    assert old_obj["properties"]["description"] == "original description"
    assert new_obj["properties"]["description"] == "modified description after cache deletion"

    group.delete()
    print(f"Deleted group {group.dn!r}.")
