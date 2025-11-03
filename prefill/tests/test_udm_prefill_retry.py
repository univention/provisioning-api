# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from test_helpers.mock_data import (
    GROUPS_TOPIC,
    MQMESSAGE_PREFILL,
    USERS_TOPIC,
)
from werkzeug.wrappers.response import Response

from univention.provisioning.backends.message_queue import MessageAckManager, QueueStatus
from univention.provisioning.prefill.config import PrefillSettings
from univention.provisioning.prefill.mq_port import MessageQueuePort
from univention.provisioning.prefill.prefill_service import PrefillService
from univention.provisioning.prefill.udm_adapter import UDMAdapter
from univention.provisioning.prefill.update_sub_q_status_port import UpdateSubscriptionsQueueStatusPort
from univention.provisioning.utils.log import setup_logging


class EscapeLoopException(Exception): ...


@register_fixture
class PrefillSettingsFactory(ModelFactory[PrefillSettings]): ...


@pytest.fixture
async def udm_prefill(httpserver, prefill_settings_factory: ModelFactory[PrefillSettings]) -> PrefillService:
    setup_logging(logging.INFO)
    settings = prefill_settings_factory.build()
    settings.udm_host = httpserver.host
    settings.udm_port = httpserver.port
    settings.udm_protocol = "http"
    settings.udm_url_path_prefix = ""
    settings.network_retry_starting_interval = 1
    settings.network_retry_max_delay = 120
    settings.network_retry_max_attempts = 4

    httpserver.expect_request("/udm/").respond_with_json(
        {"_links": {"udm:object-types": [{"name": USERS_TOPIC}, {"name": GROUPS_TOPIC}]}}
    )
    httpserver.expect_request(f"/udm/{GROUPS_TOPIC}/").respond_with_json(
        {
            "results": 4,
            "_embedded": {
                "udm:object": [
                    {"uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/1")},
                    {"uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/2")},
                    {"uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/3")},
                    {"uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/4")},
                ]
            },
        }
    )
    httpserver.expect_request(f"/udm/{GROUPS_TOPIC}/1").respond_with_json(
        {
            "_links": {},
            "uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/1"),
            "dn": "",
            "objectType": GROUPS_TOPIC,
            "position": "",
            "properties": {},
            "uuid": "",
        }
    )
    httpserver.expect_request(f"/udm/{GROUPS_TOPIC}/2").respond_with_json(
        {
            "_links": {},
            "uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/2"),
            "dn": "",
            "objectType": GROUPS_TOPIC,
            "position": "",
            "properties": {},
            "uuid": "",
        }
    )
    httpserver.expect_request(f"/udm/{GROUPS_TOPIC}/4").respond_with_json(
        {
            "_links": {},
            "uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/4"),
            "dn": "",
            "objectType": GROUPS_TOPIC,
            "position": "",
            "properties": {},
            "uuid": "",
        }
    )

    async with UDMAdapter(settings) as udm:
        mq_mock = AsyncMock(spec_set=MessageQueuePort)
        mq_mock.initialize_subscription.return_value = QueueStatus.READY
        udm_prefill = PrefillService(
            ack_manager=MessageAckManager(),
            mq=mq_mock,
            udm=udm,
            update_sub_q_status=AsyncMock(spec_set=UpdateSubscriptionsQueueStatusPort),
            settings=settings,
        )
        udm_prefill.max_prefill_attempts = 5
        yield udm_prefill


@pytest.mark.anyio
class TestUDMPreFillRetry:
    @patch("univention.provisioning.prefill.prefill_service.datetime")
    async def test_retry_prefill_udm_response_error(self, mock_datetime, udm_prefill: PrefillService, httpserver):
        mocked_date = datetime(2023, 11, 9, 11, 15, 52, 616061)
        mock_datetime.now.return_value = mocked_date
        mock_acknowledgements = AsyncMock()
        udm_prefill.mq.get_one_message = AsyncMock(
            side_effect=[
                (MQMESSAGE_PREFILL, mock_acknowledgements),
                EscapeLoopException("Stop waiting for the new event"),
            ]
        )

        retry_attempt = 0
        first_request = 0
        last_request = 0

        def check_retry(request) -> Response:
            nonlocal retry_attempt
            nonlocal first_request
            nonlocal last_request
            if retry_attempt == 0:
                first_request = time.time()

            retry_attempt += 1

            if retry_attempt < 3:
                return Response(status=404)

            last_request = time.time()
            return Response(
                json.dumps(
                    {
                        "_links": {},
                        "uri": httpserver.url_for(f"/udm/{GROUPS_TOPIC}/3"),
                        "dn": "",
                        "objectType": GROUPS_TOPIC,
                        "position": "",
                        "properties": {},
                        "uuid": "",
                    }
                ),
                mimetype="application/json",
            )

        httpserver.expect_request(f"/udm/{GROUPS_TOPIC}/3").respond_with_handler(check_retry)

        with pytest.raises(EscapeLoopException):
            await udm_prefill.handle_requests_to_prefill()

        # if 2 tries fail we wait for 3s (1 + 2)
        assert (last_request - first_request) >= 3
        assert retry_attempt == 3

    @patch("univention.provisioning.prefill.prefill_service.datetime")
    async def test_retry_prefill_udm_connection_error(self, mock_datetime, udm_prefill: PrefillService, httpserver):
        start = time.time()
        httpserver.stop()

        mocked_date = datetime(2023, 11, 9, 11, 15, 52, 616061)
        mock_datetime.now.return_value = mocked_date
        mock_acknowledgements = AsyncMock()
        udm_prefill.mq.get_one_message = AsyncMock(
            side_effect=[
                (MQMESSAGE_PREFILL, mock_acknowledgements),
                EscapeLoopException("Stop waiting for the new event"),
            ]
        )

        with pytest.raises(ExceptionGroup):
            await udm_prefill.handle_requests_to_prefill()

        end = time.time()
        # if 3 tries fail we wait for 7s (1 + 2 + 4)
        assert (end - start) >= 7
