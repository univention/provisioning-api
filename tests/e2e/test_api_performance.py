# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from typing import Any, AsyncGenerator, Callable, Coroutine, Literal

import pytest

from server.adapters.nats_adapter import NatsKeys
from univention.admin.rest.client import UDM, time
from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.api import MessageProcessingStatus, MessageProcessingStatusReport
from univention.provisioning.models.subscription import FillQueueStatus

from tests.conftest import DUMMY_REALMS_TOPICS, REALMS_TOPICS
from tests.e2e.conftest import E2ETestSettings
from tests.e2e.helpers import create_message_via_events_api, create_message_via_udm_rest_api

EXPECTED_AVG_DELAY = 50
EXPECTED_MAX_DELAY = 150


def print_stats(durations: list[float]) -> None:
    print(f"all request times were: {durations}")
    print(f"minimum request time: {min(durations):.2f}ms")
    print(f"maximum request time: {max(durations):.2f}ms")
    print(f"average request time: {sum(durations) / len(durations):.2f}ms")


@pytest.fixture
def realms_topics(request) -> Literal:
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
    provisioning_client: ProvisioningConsumerClient,
    subscription: str,
    test_settings: E2ETestSettings,
    purge_stream: Callable[[str], Coroutine[Any, Any, None]],
):
    test_number = 10
    get_durations = []
    status_durations = []
    messages = []
    responses = []

    print("Cleaning up consumer stream")
    await purge_stream(NatsKeys.stream(subscription))

    print("Adding simple messages to the incoming queue")
    for _ in range(test_number):
        messages.append(create_message_via_events_api(test_settings))

    await asyncio.sleep(1)

    print("Starting the test run")
    for i in range(test_number):
        tic = time.perf_counter()
        response = await provisioning_client.get_subscription_message(
            name=subscription,
        )
        get_durations.append((time.perf_counter() - tic) * 1000)

        assert response.body == messages[i]
        responses.append(response)
        print(f"request time was {get_durations[-1]:.2f}")

        tic = time.perf_counter()
        await provisioning_client.set_message_status(
            subscription,
            MessageProcessingStatusReport(status=MessageProcessingStatus.ok, message_seq_num=response.sequence_number),
        )
        status_durations.append((time.perf_counter() - tic) * 1000)

    print("get_subscription_message statistics")
    print_stats(get_durations)
    print("set_message_status statistics")
    print_stats(status_durations)

    avg = sum(get_durations) / len(get_durations)
    assert avg < EXPECTED_AVG_DELAY, f"average request duration was higher than {EXPECTED_AVG_DELAY} ms: {avg} ms."
    max_d = max(get_durations)
    assert max_d < EXPECTED_MAX_DELAY, f"maximum request duration was higher than {EXPECTED_MAX_DELAY} ms: {max_d}"


@pytest.mark.parametrize("realms_topics", [REALMS_TOPICS], indirect=["realms_topics"])
@pytest.mark.parametrize("subscription", [False, True], indirect=True, ids=["without_prefill", "with_prefill"])
async def test_udm_message_timing(
    provisioning_client: ProvisioningConsumerClient,
    subscription: str,
    udm: UDM,
    purge_stream: Callable[[str], Coroutine[Any, Any, None]],
):
    test_number = 10
    get_durations = []
    status_durations = []
    messages = []
    responses = []

    print("Cleaning up consumer stream")
    await purge_stream(NatsKeys.stream(subscription))

    print("Adding udm messages to the incoming queue")
    for _ in range(test_number):
        messages.append(create_message_via_udm_rest_api(udm))  # noqa: F841

    await asyncio.sleep(1)

    print("Starting the test run")
    for i in range(test_number):
        tic = time.perf_counter()
        response = await provisioning_client.get_subscription_message(
            name=subscription,
        )
        assert response.body.new["dn"] == messages[i].dn
        responses.append(response)
        get_durations.append((time.perf_counter() - tic) * 1000)
        print(f"request time was {get_durations[-1]:.2f}")

        tic = time.perf_counter()
        await provisioning_client.set_message_status(
            subscription,
            MessageProcessingStatusReport(status=MessageProcessingStatus.ok, message_seq_num=response.sequence_number),
        )
        status_durations.append((time.perf_counter() - tic) * 1000)

    print("get_subscription_message statistics")
    print_stats(get_durations)
    print("set_message_status statistics")
    print_stats(status_durations)

    avg = sum(get_durations) / len(get_durations)
    assert avg < EXPECTED_AVG_DELAY, f"average request duration was higher than {EXPECTED_AVG_DELAY} ms: {avg} ms."
    max_d = max(get_durations)
    assert max_d < EXPECTED_MAX_DELAY, f"maximum request duration was higher than {EXPECTED_MAX_DELAY} ms: {max_d}"
