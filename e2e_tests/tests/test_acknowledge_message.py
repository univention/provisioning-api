# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import time

from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.message import MessageProcessingStatus


async def test_get_multiple_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    body_1 = create_message_via_events_api(test_settings)
    body_2 = create_message_via_events_api(test_settings)

    for body in [body_1, body_2]:
        message = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)
        assert message.body == body
        await provisioning_client.set_message_status(
            dummy_subscription, message.sequence_number, MessageProcessingStatus.ok
        )


async def test_acknowledge_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)

    message = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)

    assert message.body == body

    await provisioning_client.set_message_status(
        dummy_subscription, message.sequence_number, MessageProcessingStatus.ok
    )

    response2 = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=35)

    # Sometimes other messages like the "DC Backup Hosts" group can sneak into the queue
    # The test is considered successful if the response is empty, or if the response is not a redelivery
    # of the previous message
    if response2:
        assert response2.body != body


async def test_do_not_acknowledge_message(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # test the first delivery of a message
    message = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)
    assert message.body == body

    # the same unacknowledged message is redelivered after ack_wait expires
    message2 = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)
    assert message2.body == body


async def test_unacknowledged_message_is_redelivered_quickly(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    """Regression test for the 30s NATS hang (univention/dev/internal/team-nubus#1370).

    With ``max_ack_pending=1`` a fetched-but-unacknowledged message blocks all
    further delivery until its ack_wait expires. Before the fix the consumer
    queue used the NATS default of 30s, so the next fetch returned null and the
    client appeared to hang for up to 30s. The fix lowers ConsumerQueue.ack_wait
    to 1s, so the message is redelivered almost immediately.

    A regression to the 30s default makes ``elapsed`` jump to ~30s (or the fetch
    returns None within the poll window), failing this test.
    """
    # Get one delivered, unacknowledged message. The dispatcher refreshes its
    # subscription mapping on an interval, so an event posted before the freshly
    # created subscription is in that mapping is dropped ("No consumers"); and a
    # fresh subscription's first request drains the (empty) prefill queue. Both are
    # unrelated to ack_wait, so re-post and poll until a message is actually in hand.
    first = None
    deadline = time.monotonic() + 60
    while first is None and time.monotonic() < deadline:
        create_message_via_events_api(test_settings)
        for _ in range(2):
            first = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)
            if first is not None:
                break
    assert first is not None, "message was never delivered (dispatcher subscription-mapping race?)"

    # Do NOT acknowledge. With max_ack_pending=1 the next fetch is blocked until
    # ack_wait expires, then the SAME message is redelivered. Measure how long.
    start = time.monotonic()
    redelivered = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=30)
    elapsed = time.monotonic() - start

    assert redelivered is not None, "message was not redelivered within 30s (NATS hang regression)"
    assert redelivered.sequence_number == first.sequence_number
    assert elapsed < 10, f"redelivery took {elapsed:.1f}s; expected ~1s (ack_wait=1), regressed to 30s default?"
