# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest

from admin.service import AdminService
from admin.service.admin import SUBSCRIPTIONS
from shared.models import NewSubscription, Subscription
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
    )

    async def test_get_subscriptions(self, admin_service: AdminService):
        admin_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        admin_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        subscription = Subscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=[REALMS_TOPICS_STR],
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await admin_service.get_subscriptions()

        admin_service._port.get_list_value.assert_called_once_with(SUBSCRIPTIONS)
        admin_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == [subscription]

    async def test_get_subscriptions_empty_result(self, admin_service: AdminService):
        admin_service._port.get_list_value = AsyncMock(return_value=[])

        result = await admin_service.get_subscriptions()

        admin_service._port.get_list_value.assert_called_once_with(SUBSCRIPTIONS)
        assert result == []

    async def test_create_subscription_existing_subscription(
        self, admin_service: AdminService
    ):
        admin_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        with pytest.raises(ValueError) as e:
            await admin_service.register_subscription(self.new_subscription)

        admin_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        admin_service._port.put_value.assert_not_called()
        assert "Subscription with the given name already exists" == str(e.value)

    async def test_add_subscription(self, admin_service: AdminService):
        admin_service._port.get_dict_value = AsyncMock(return_value=None)
        admin_service._port.get_str_value = AsyncMock(side_effect=[None, None])
        admin_service._port.create_stream = AsyncMock()
        admin_service._port.create_consumer = AsyncMock()

        await admin_service.register_subscription(self.new_subscription)

        admin_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        admin_service._port.get_str_value.assert_has_calls(
            [call(SUBSCRIPTIONS), call("udm:groups/group")]
        )
        admin_service._port.put_value.assert_has_calls(
            [
                call(SUBSCRIPTIONS, SUBSCRIPTION_NAME),
                call("udm:groups/group", SUBSCRIPTION_NAME),
            ]
        )
