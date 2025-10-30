# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import pytest
from nats.js.api import RetentionPolicy
from nats.js.errors import BadRequestError, ServerError

from univention.provisioning.backends.nats_mq import ConsumerQueue, NatsMessageQueue

from .e2e_settings import E2ETestSettings


@pytest.fixture
async def nats_mq_adapter(test_settings: E2ETestSettings):
    nats_adapter = NatsMessageQueue(test_settings.nats_url, test_settings.nats_user, test_settings.nats_password, 1)
    await nats_adapter.connect()
    yield nats_adapter
    await nats_adapter.close()


@pytest.fixture
async def test_queue(nats_mq_adapter: NatsMessageQueue):
    stream_name = "just_testing_again"
    queue = ConsumerQueue(stream_name)
    queue.retention_policy = RetentionPolicy.WORK_QUEUE
    await nats_mq_adapter.ensure_stream(queue)
    yield queue
    await nats_mq_adapter.delete_stream(queue)


@pytest.fixture
async def test_consumer(nats_mq_adapter: NatsMessageQueue, test_queue: ConsumerQueue):
    await nats_mq_adapter.ensure_consumer(test_queue)
    yield True
    await nats_mq_adapter.delete_consumer(test_queue)


async def test_nats_connection(nats_mq_adapter: NatsMessageQueue):
    assert nats_mq_adapter


async def test_ensure_stream(nats_mq_adapter: NatsMessageQueue, test_queue: ConsumerQueue):
    await nats_mq_adapter.ensure_stream(test_queue)
    await nats_mq_adapter.ensure_stream(test_queue)
    await nats_mq_adapter.ensure_stream(test_queue)


async def test_ensure_stream_with_filter(nats_mq_adapter: NatsMessageQueue):
    queue = ConsumerQueue("just_testing")
    await nats_mq_adapter.ensure_stream(queue)
    await nats_mq_adapter.delete_stream(queue)


async def test_ensure_stream_with_conflicting_filters(nats_mq_adapter: NatsMessageQueue):
    queue = ConsumerQueue("just_testing")
    await nats_mq_adapter.ensure_stream(queue)
    with pytest.raises(BadRequestError):
        queue2 = ConsumerQueue("just_testing2")
        queue2.subjects = ["*"]
        await nats_mq_adapter.ensure_stream(queue2)
    await nats_mq_adapter.delete_stream(queue)


async def test_update_stream_subject(nats_mq_adapter: NatsMessageQueue, test_queue: ConsumerQueue):
    test_queue.subjects = [str(uuid.uuid4)[:8]]
    await nats_mq_adapter.ensure_stream(test_queue)
    stream_info = await nats_mq_adapter._js.stream_info(test_queue.queue_name)
    assert stream_info.config.subjects != [test_queue.queue_name]


async def test_update_stream_retention(nats_mq_adapter: NatsMessageQueue, test_queue: ConsumerQueue):
    test_queue.retention_policy = RetentionPolicy.LIMITS
    with pytest.raises(ServerError):
        await nats_mq_adapter.ensure_stream(test_queue)


async def test_ensure_consumer(test_consumer: bool):
    assert test_consumer


async def test_ensure_consumer_with_name(nats_mq_adapter: NatsMessageQueue, test_queue, test_consumer):
    await nats_mq_adapter.ensure_consumer(test_queue)
    await nats_mq_adapter.ensure_consumer(test_queue)
