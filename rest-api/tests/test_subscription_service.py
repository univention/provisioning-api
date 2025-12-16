# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call

import pytest
from fastapi import HTTPException, status
from test_helpers.mock_data import (
    CONSUMER_HASHED_PASSWORD,
    GROUPS_REALMS_TOPICS,
    GROUPS_TOPIC,
    REALM,
    SUBSCRIPTION_INFO,
    SUBSCRIPTION_NAME,
    USERS_TOPIC,
    SUBSCRIPTION_INFO_dumpable,
)

from univention.provisioning.backends.nats_kv import NatsKeyValueDB
from univention.provisioning.backends.nats_mq import ConsumerQueue
from univention.provisioning.models.constants import BucketName
from univention.provisioning.models.message import RealmTopic
from univention.provisioning.models.subscription import FillQueueStatus, NewSubscription, Subscription
from univention.provisioning.rest.config import AppSettings
from univention.provisioning.rest.mq_port import MessageQueuePort
from univention.provisioning.rest.subscription_service import SubscriptionService
from univention.provisioning.rest.subscriptions_db_adapter_nats import NatsSubscriptionsDB


@pytest.fixture
def sub_service() -> SubscriptionService:
    service = SubscriptionService(
        subscriptions_db=NatsSubscriptionsDB(AsyncMock(spec_set=AppSettings)), mq=AsyncMock(spec_set=MessageQueuePort)
    )
    service.sub_db.kv = AsyncMock(spec_set=NatsKeyValueDB)
    return service


@pytest.mark.anyio
class TestSubscriptionService:
    new_subscription = NewSubscription(
        name=SUBSCRIPTION_NAME,
        realms_topics=GROUPS_REALMS_TOPICS,
        request_prefill=True,
        password="password",
    )

    async def test_get_subscriptions(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_bucket_keys = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        subscription = Subscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await sub_service.get_subscriptions()

        sub_service.sub_db.get_bucket_keys.assert_called_once_with(BucketName.credentials)
        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        assert result == [subscription]

    async def test_get_subscriptions_empty_result(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_bucket_keys = AsyncMock(return_value=[])

        result = await sub_service.get_subscriptions()

        sub_service.sub_db.get_bucket_keys.assert_called_once_with(BucketName.credentials)
        assert result == []

    async def test_create_subscription_existing_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service.sub_db.get_str_value = AsyncMock(return_value=CONSUMER_HASHED_PASSWORD)
        sub_service.sub_db.put_value = AsyncMock(return_value=None)

        result = await sub_service.register_subscription(self.new_subscription)

        assert result is False
        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.get_str_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.credentials)
        sub_service.sub_db.put_value.assert_not_called()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("request_prefill", False),
            ("password", "wrong_password"),
            (
                "realms_topics",
                [RealmTopic(realm=REALM, topic=GROUPS_TOPIC), RealmTopic(realm=REALM, topic=USERS_TOPIC)],
            ),
        ],
    )
    async def test_create_subscription_existing_subscription_different_parameters(
        self, field, value, sub_service: SubscriptionService
    ):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service.sub_db.get_str_value = AsyncMock(return_value=CONSUMER_HASHED_PASSWORD)
        sub_service.sub_db.put_value = AsyncMock(return_value=None)

        new_sub = deepcopy(self.new_subscription)

        setattr(new_sub, field, value)
        with pytest.raises(HTTPException):
            await sub_service.register_subscription(new_sub)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.put_value.assert_not_called()

    async def test_add_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=None)
        sub_service.sub_db.get_list_value = AsyncMock(return_value=[])
        sub_service.sub_db.put_value = AsyncMock(return_value=None)
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock()

        await sub_service.register_subscription(self.new_subscription)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        assert sub_service.sub_db.put_value.call_count == 2  # credentials, subscription

    async def test_get_subscription_not_found(self, sub_service):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=f"Subscription not found: {SUBSCRIPTION_NAME!r}"):
            await sub_service.get_subscription(SUBSCRIPTION_NAME)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)

    async def test_get_subscription_queue_status_with_no_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=f"Subscription not found: {SUBSCRIPTION_NAME!r}"):
            await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)

    async def test_get_subscription_queue_status_with_subscriptions(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        assert result == FillQueueStatus.done

    async def test_set_subscription_queue_status_with_no_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=None)
        sub_service.sub_db.put_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=f"Subscription not found: {SUBSCRIPTION_NAME!r}"):
            await sub_service.set_subscription_queue_status(SUBSCRIPTION_NAME, FillQueueStatus.pending)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.put_value.assert_not_called()

    async def test_set_subscription_queue_status_with_subscriptions(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service.sub_db.put_value = AsyncMock(return_value=None)
        result = await sub_service.set_subscription_queue_status(SUBSCRIPTION_NAME, FillQueueStatus.pending)

        sub_info = deepcopy(SUBSCRIPTION_INFO_dumpable)
        sub_info["prefill_queue_status"] = "pending"

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.put_value.assert_called_once_with(SUBSCRIPTION_NAME, sub_info, BucketName.subscriptions)
        assert result is None

    async def test_delete_subscription_with_no_existing_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=None)
        sub_service.sub_db.put_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match=f"Subscription not found: {SUBSCRIPTION_NAME!r}"):
            await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.put_value.assert_not_called()

    async def test_delete_subscription(self, sub_service: SubscriptionService):
        sub_service.sub_db.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service.sub_db.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        sub_service.sub_db.delete_kv_pair = AsyncMock(return_value=None)

        await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service.sub_db.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, BucketName.subscriptions)
        sub_service.sub_db.delete_kv_pair.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, BucketName.credentials),
                call(SUBSCRIPTION_NAME, BucketName.subscriptions),
            ]
        )

    async def test_prepare_and_store_subscription_info_success_with_prefill(self, sub_service: SubscriptionService):
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock()
        sub_service.sub_db.store_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            password="password",
        )

        await sub_service.prepare_and_store_subscription_info(new_sub)

        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.store_subscription.assert_called_once()

        # Verify the subscription object passed to store_subscription
        call_args = sub_service.sub_db.store_subscription.call_args
        assert call_args[0][0] == SUBSCRIPTION_NAME
        stored_subscription = call_args[0][1]
        assert stored_subscription.name == SUBSCRIPTION_NAME
        assert stored_subscription.realms_topics == GROUPS_REALMS_TOPICS
        assert stored_subscription.request_prefill is True
        assert stored_subscription.prefill_queue_status == FillQueueStatus.pending

    async def test_prepare_and_store_subscription_info_success_without_prefill(self, sub_service: SubscriptionService):
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock()
        sub_service.sub_db.store_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=False,
            password="password",
        )

        await sub_service.prepare_and_store_subscription_info(new_sub)

        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.store_subscription.assert_called_once()

        # Verify the subscription object has correct prefill status
        call_args = sub_service.sub_db.store_subscription.call_args
        stored_subscription = call_args[0][1]
        assert stored_subscription.prefill_queue_status == FillQueueStatus.done

    async def test_prepare_and_store_subscription_info_queue_creation_fails(self, sub_service: SubscriptionService):
        sub_service.mq.create_queue = AsyncMock(side_effect=Exception("Queue creation failed"))
        sub_service.mq.create_consumer = AsyncMock()
        sub_service.mq.delete_queue = AsyncMock()
        sub_service.mq.delete_consumer = AsyncMock()
        sub_service.sub_db.store_subscription = AsyncMock()
        sub_service.sub_db.delete_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            password="password",
        )

        with pytest.raises(HTTPException) as exc_info:
            await sub_service.prepare_and_store_subscription_info(new_sub)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "internal error" in exc_info.value.detail

        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_not_called()
        sub_service.sub_db.store_subscription.assert_not_called()

        # No rollback needed since nothing was created
        sub_service.mq.delete_queue.assert_not_called()
        sub_service.mq.delete_consumer.assert_not_called()
        sub_service.sub_db.delete_subscription.assert_not_called()

    async def test_prepare_and_store_subscription_info_consumer_creation_fails(self, sub_service: SubscriptionService):
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock(side_effect=Exception("Consumer creation failed"))
        sub_service.mq.delete_queue = AsyncMock()
        sub_service.mq.delete_consumer = AsyncMock()
        sub_service.sub_db.store_subscription = AsyncMock()
        sub_service.sub_db.delete_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            password="password",
        )

        with pytest.raises(HTTPException) as exc_info:
            await sub_service.prepare_and_store_subscription_info(new_sub)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.store_subscription.assert_not_called()

        # Queue should be rolled back
        sub_service.mq.delete_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.delete_consumer.assert_not_called()  # Consumer wasn't created
        sub_service.sub_db.delete_subscription.assert_not_called()

    async def test_prepare_and_store_subscription_info_subscription_storage_fails(
        self, sub_service: SubscriptionService
    ):
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock()
        sub_service.mq.delete_queue = AsyncMock()
        sub_service.mq.delete_consumer = AsyncMock()
        sub_service.sub_db.store_subscription = AsyncMock(side_effect=Exception("Storage failed"))
        sub_service.sub_db.delete_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            password="password",
        )

        with pytest.raises(HTTPException) as exc_info:
            await sub_service.prepare_and_store_subscription_info(new_sub)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.store_subscription.assert_called_once()

        # Both queue and consumer should be rolled back
        sub_service.mq.delete_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.delete_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.delete_subscription.assert_not_called()  # Storage failed, so nothing to delete

    async def test_prepare_and_store_subscription_info_rollback_failures(self, sub_service: SubscriptionService):
        sub_service.mq.create_queue = AsyncMock()
        sub_service.mq.create_consumer = AsyncMock()
        sub_service.mq.delete_queue = AsyncMock(side_effect=Exception("Rollback failed"))
        sub_service.mq.delete_consumer = AsyncMock(side_effect=Exception("Rollback failed"))
        sub_service.sub_db.store_subscription = AsyncMock(side_effect=Exception("Storage failed"))
        sub_service.sub_db.delete_subscription = AsyncMock()

        new_sub = NewSubscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=GROUPS_REALMS_TOPICS,
            request_prefill=True,
            password="password",
        )

        # Even if rollback fails, the original exception should still be raised
        with pytest.raises(HTTPException) as exc_info:
            await sub_service.prepare_and_store_subscription_info(new_sub)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "internal error" in exc_info.value.detail

        # Verify all operations were attempted
        sub_service.mq.create_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.create_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.sub_db.store_subscription.assert_called_once()

        # Verify rollback was attempted despite failures
        sub_service.mq.delete_consumer.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
        sub_service.mq.delete_queue.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME))
