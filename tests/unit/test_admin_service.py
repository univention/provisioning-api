# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest
from fastapi import HTTPException

from admin.service import AdminService
from shared.models import NewSubscription, Subscription
from shared.models.subscription import Bucket
from tests.conftest import (
    SUBSCRIPTION_NAME,
    REALMS_TOPICS,
    REALMS_TOPICS_STR,
    SUBSCRIPTION_INFO,
)


@pytest.fixture
def admin_service() -> AdminService:
    return AdminService(AsyncMock())


@pytest.mark.anyio
class TestAdminService:
    new_subscription = NewSubscription(
        name=SUBSCRIPTION_NAME,
        realms_topics=REALMS_TOPICS,
        request_prefill=True,
        password="password",
    )
    hashed_password = "$2b$12$G56ltBheLThdzppmOX.bcuAdZ.Ffx65oo7Elc.OChmzENtXtA1iSe"

    async def test_get_subscriptions(self, admin_service: AdminService):
        admin_service._port.get_bucket_keys = AsyncMock(
            return_value=[SUBSCRIPTION_NAME]
        )
        admin_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        subscription = Subscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=[REALMS_TOPICS_STR],
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await admin_service.get_subscriptions()

        admin_service._port.get_bucket_keys.assert_called_once_with(Bucket.credentials)
        admin_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        assert result == [subscription]

    async def test_get_subscriptions_empty_result(self, admin_service: AdminService):
        admin_service._port.get_bucket_keys = AsyncMock(return_value=[])

        result = await admin_service.get_subscriptions()

        admin_service._port.get_bucket_keys.assert_called_once_with(Bucket.credentials)
        assert result == []

    async def test_create_subscription_existing_subscription(
        self, admin_service: AdminService
    ):
        admin_service._port.get_str_value = AsyncMock(return_value=self.hashed_password)

        with pytest.raises(HTTPException):
            await admin_service.register_subscription(self.new_subscription)

        admin_service._port.get_str_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.credentials
        )
        admin_service._port.put_value.assert_not_called()

    async def test_add_subscription(self, admin_service: AdminService):
        admin_service._port.get_str_value = AsyncMock(side_effect=[None, None, None])
        admin_service._port.create_stream = AsyncMock()
        admin_service._port.create_consumer = AsyncMock()

        await admin_service.register_subscription(self.new_subscription)

        admin_service._port.get_str_value.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, Bucket.credentials),
                call("udm:groups/group", Bucket.subscriptions),
            ]
        )
        assert admin_service._port.put_value.call_count == 3
