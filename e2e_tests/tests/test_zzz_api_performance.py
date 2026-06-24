# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from typing import Any, AsyncGenerator, Callable, Coroutine

import pytest

from univention.admin.rest.client import UDM, time
from univention.provisioning.backends.nats_mq import ConsumerQueue
from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.message import MessageProcessingStatus
from univention.provisioning.models.subscription import FillQueueStatus, RealmTopic

from .e2e_settings import E2ETestSettings
from .mock_data import DUMMY_REALMS_TOPICS, USERS_REALMS_TOPICS

EXPECTED_AVG_DELAY = 50
EXPECTED_MAX_DELAY = 150
# Number of get/ack round-trips to perform before measuring, to prime connections
# and warm any lazily-initialized caches so the first measured request isn't an outlier.
WARMUP_REQUESTS = 5


def print_stats(durations: list[float]) -> None:
    # print(f"all request times were: {durations}")
    print(f"minimum request time: {min(durations):.2f}ms")
    print(f"maximum request time: {max(durations):.2f}ms")
    print(f"average request time: {sum(durations) / len(durations):.2f}ms")


def print_throughput(count: int, elapsed_seconds: float) -> None:
    print(f"processed {count} messages in {elapsed_seconds:.2f}s")
    print(f"throughput: {count / elapsed_seconds:.1f} messages/second")
    print(f"average per-message time (get + ack): {elapsed_seconds / count * 1000:.2f}ms")


@pytest.fixture
def realms_topics(request) -> list[RealmTopic]:
    return getattr(request, "param", DUMMY_REALMS_TOPICS)


@pytest.fixture
async def subscription(
    request,
    realms_topics,
    subscriber_name,
    subscriber_password,
    provisioning_admin_client: ProvisioningConsumerClient,
    provisioning_client: ProvisioningConsumerClient,
) -> AsyncGenerator[str, Any]:
    request_prefill = getattr(request, "param", False)
    await provisioning_admin_client.create_subscription(
        name=subscriber_name, password=subscriber_password, realms_topics=realms_topics, request_prefill=request_prefill
    )

    # ensure that the pre-fill process is finished successfully
    for _ in range(25):
        subscription = await provisioning_client.get_subscription(subscriber_name)

        assert subscription.prefill_queue_status != FillQueueStatus.failed

        if subscription.prefill_queue_status == FillQueueStatus.done:
            break
        print("Waiting for prefill to be finished")
        await asyncio.sleep(0.2)
    else:
        assert False, "prefill was not done within 10 seconds"

    yield subscriber_name

    await provisioning_admin_client.cancel_subscription(subscriber_name)


@pytest.mark.parametrize(
    "subscription", [False, True], indirect=["subscription"], ids=["without_prefill", "with_prefill"]
)
async def test_simple_message_timing(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    subscription: str,
    test_settings: E2ETestSettings,
    purge_stream: Callable[[str], Coroutine[Any, Any, None]],
):
    test_number = 2_000
    get_durations = []
    status_durations = []
    total_durations = []
    messages = []
    responses = []
    queue = ConsumerQueue(subscription)
    print("Cleaning up consumer stream")
    await purge_stream(queue.queue_name)

    print("Adding simple messages to the incoming queue")
    # Add extra messages to be consumed during warmup so the measured run still
    # processes the full `test_number` of messages.
    for _ in range(test_number + WARMUP_REQUESTS):
        messages.append(create_message_via_events_api(test_settings))

    await asyncio.sleep(1)

    # Warmup: consume and acknowledge the first messages. Acknowledging is required so
    # they don't stay pending and get redelivered into the measured run below.
    for i in range(WARMUP_REQUESTS):
        response = await provisioning_client.get_subscription_message(name=subscription)
        assert response.body == messages[i]
        await provisioning_client.set_message_status(
            subscription, response.sequence_number, status=MessageProcessingStatus.ok
        )

    print("Starting the test run")
    run_start = time.perf_counter()
    for i in range(test_number):
        msg_tic = time.perf_counter()
        response = await provisioning_client.get_subscription_message(name=subscription)
        get_durations.append((time.perf_counter() - msg_tic) * 1000)

        assert response.body == messages[WARMUP_REQUESTS + i]
        responses.append(response)
        # print(f"request time was {get_durations[-1]:.2f}")

        status_tic = time.perf_counter()
        await provisioning_client.set_message_status(
            subscription, response.sequence_number, status=MessageProcessingStatus.ok
        )
        status_durations.append((time.perf_counter() - status_tic) * 1000)
        # full per-message cycle: get + assert + ack and everything in between
        total_durations.append((time.perf_counter() - msg_tic) * 1000)
    run_elapsed = time.perf_counter() - run_start

    print("get_subscription_message statistics")
    print_stats(get_durations)
    print("set_message_status statistics")
    print_stats(status_durations)
    print("full per-message (get + ack) statistics")
    print_stats(total_durations)
    print_throughput(test_number, run_elapsed)

    avg = sum(get_durations) / len(get_durations)
    assert avg < EXPECTED_AVG_DELAY, f"average request duration was higher than {EXPECTED_AVG_DELAY} ms: {avg} ms."
    max_d = max(get_durations)
    assert max_d < EXPECTED_MAX_DELAY, f"maximum request duration was higher than {EXPECTED_MAX_DELAY} ms: {max_d}"


@pytest.mark.parametrize("realms_topics", [USERS_REALMS_TOPICS], indirect=["realms_topics"])
@pytest.mark.parametrize("subscription", [False, True], indirect=True, ids=["without_prefill", "with_prefill"])
async def test_udm_message_timing(
    create_user_via_udm_rest_api,
    provisioning_client: ProvisioningConsumerClient,
    subscription: str,
    realms_topics: list[RealmTopic],
    udm: UDM,
    purge_stream: Callable[[str], Coroutine[Any, Any, None]],
):
    test_number = 1000
    get_durations = []
    status_durations = []
    total_durations = []
    messages = []
    responses = []
    queue = ConsumerQueue(subscription)
    print("Cleaning up consumer stream")
    await purge_stream(queue.queue_name)

    print("Adding udm messages to the incoming queue")
    # Add extra messages to be consumed during warmup so the measured run still
    # processes the full `test_number` of messages.
    for _ in range(test_number + WARMUP_REQUESTS):
        messages.append(create_user_via_udm_rest_api())  # noqa: F841

    await asyncio.sleep(1)

    # Warmup: consume and acknowledge the first messages. Acknowledging is required so
    # they don't stay pending and get redelivered into the measured run below.
    for i in range(WARMUP_REQUESTS):
        response = await provisioning_client.get_subscription_message(name=subscription)
        assert response.body.new["dn"] == messages[i].dn
        await provisioning_client.set_message_status(subscription, response.sequence_number, MessageProcessingStatus.ok)

    print("Starting the test run")
    run_start = time.perf_counter()
    for i in range(test_number):
        msg_tic = time.perf_counter()
        response = await provisioning_client.get_subscription_message(name=subscription)
        get_durations.append((time.perf_counter() - msg_tic) * 1000)
        assert response.body.new["dn"] == messages[WARMUP_REQUESTS + i].dn
        responses.append(response)
        # print(f"request time was {get_durations[-1]:.2f}")

        status_tic = time.perf_counter()
        await provisioning_client.set_message_status(subscription, response.sequence_number, MessageProcessingStatus.ok)
        status_durations.append((time.perf_counter() - status_tic) * 1000)
        # full per-message cycle: get + assert + ack and everything in between
        total_durations.append((time.perf_counter() - msg_tic) * 1000)
    run_elapsed = time.perf_counter() - run_start

    print("get_subscription_message statistics")
    print_stats(get_durations)
    print("set_message_status statistics")
    print_stats(status_durations)
    print("full per-message (get + ack) statistics")
    print_stats(total_durations)
    print_throughput(test_number, run_elapsed)

    avg = sum(get_durations) / len(get_durations)
    assert avg < EXPECTED_AVG_DELAY, f"average request duration was higher than {EXPECTED_AVG_DELAY} ms: {avg} ms."
    max_d = max(get_durations)
    assert max_d < EXPECTED_MAX_DELAY, f"maximum request duration was higher than {EXPECTED_MAX_DELAY} ms: {max_d}"
