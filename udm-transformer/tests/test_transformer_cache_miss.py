# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from univention.provisioning.udm_transformer.transformer_service import TransformerService


@pytest.fixture
def mock_cache():
    cache = AsyncMock()
    cache.retrieve = AsyncMock(return_value={})
    cache.store = AsyncMock()
    return cache


@pytest.fixture
def mock_ldap2udm():
    ldap2udm = Mock()
    ldap2udm.ldap_to_udm = Mock(
        return_value={
            "dn": "cn=test-group,cn=groups,dc=example,dc=com",
            "uuid": "test-uuid-123",
            "objectType": "groups/group",
            "properties": {"name": "test-group"},
        }
    )
    ldap2udm.reload_udm_if_required = Mock()
    return ldap2udm


@pytest.fixture
def mock_event_sender():
    sender = AsyncMock()
    sender.send_event = AsyncMock()
    return sender


@pytest.fixture
def mock_ack_manager():
    return AsyncMock()


@pytest.fixture
def mock_subscriptions():
    return AsyncMock()


@pytest.fixture
def mock_settings():
    from univention.provisioning.models.constants import PublisherName
    from univention.provisioning.udm_transformer.config import UDMTransformerSettings

    return UDMTransformerSettings(
        log_level="DEBUG",
        nats_user="test_user",
        nats_password="test_password",
        nats_host="localhost",
        nats_port=4222,
        ldap_publisher_name=PublisherName.udm_listener,
        events_username_udm="test_events",
        events_password_udm="test_events_pw",
        udm_url="http://localhost:9979/udm",
        udm_username="cn=admin",
        udm_password="test_ldap_pw",
        udm_needs_reload=True,
        provisioning_api_host="localhost",
        provisioning_api_port=8000,
    )


@pytest.fixture
def transformer_service(
    mock_ack_manager, mock_cache, mock_event_sender, mock_ldap2udm, mock_subscriptions, mock_settings
):
    return TransformerService(
        ack_manager=mock_ack_manager,
        cache=mock_cache,
        event_sender=mock_event_sender,
        ldap2udm=mock_ldap2udm,
        subscriptions=mock_subscriptions,
        settings=mock_settings,
    )


@pytest.mark.anyio
async def test_old_ldap_to_udm_obj_cache_miss(transformer_service, mock_cache, mock_ldap2udm, caplog):
    import logging

    caplog.set_level(logging.INFO)

    old_ldap_obj = {
        "entryUUID": [b"test-uuid-123"],
        "entryDN": [b"cn=test-group,cn=groups,dc=example,dc=com"],
        "univentionObjectType": [b"groups/group"],
        "cn": [b"test-group"],
    }

    mock_cache.retrieve.return_value = {}

    result = await transformer_service.old_ldap_to_udm_obj(old_ldap_obj)

    mock_cache.retrieve.assert_called_once_with("test-uuid-123")
    mock_ldap2udm.ldap_to_udm.assert_called_once_with(old_ldap_obj)

    assert result == {
        "dn": "cn=test-group,cn=groups,dc=example,dc=com",
        "uuid": "test-uuid-123",
        "objectType": "groups/group",
        "properties": {"name": "test-group"},
    }

    assert "Did not find old_ldap_object in the cache" in caplog.text


@pytest.mark.anyio
async def test_old_ldap_to_udm_obj_cache_hit(transformer_service, mock_cache, mock_ldap2udm):
    old_ldap_obj = {
        "entryUUID": [b"test-uuid-456"],
        "entryDN": [b"cn=cached-group,cn=groups,dc=example,dc=com"],
    }

    cached_obj = {
        "dn": "cn=cached-group,cn=groups,dc=example,dc=com",
        "uuid": "test-uuid-456",
        "objectType": "groups/group",
        "properties": {"name": "cached-group"},
    }
    mock_cache.retrieve.return_value = cached_obj

    result = await transformer_service.old_ldap_to_udm_obj(old_ldap_obj)

    mock_cache.retrieve.assert_called_once_with("test-uuid-456")
    mock_ldap2udm.ldap_to_udm.assert_not_called()

    assert result == cached_obj


@pytest.mark.anyio
async def test_old_ldap_to_udm_obj_cache_miss_and_transform_fails(transformer_service, mock_cache, mock_ldap2udm):
    old_ldap_obj = {
        "entryUUID": [b"test-uuid-error"],
        "entryDN": [b"cn=error-group,cn=groups,dc=example,dc=com"],
    }

    mock_cache.retrieve.return_value = {}
    mock_ldap2udm.ldap_to_udm.return_value = {}

    with pytest.raises(RuntimeError, match="Cannot live transform old ldap object"):
        await transformer_service.old_ldap_to_udm_obj(old_ldap_obj)


@pytest.mark.anyio
async def test_handle_change_with_cache_miss(transformer_service, mock_cache, mock_ldap2udm, mock_event_sender):
    old_ldap_obj = {
        "entryUUID": [b"test-uuid-789"],
        "entryDN": [b"cn=modified-group,cn=groups,dc=example,dc=com"],
        "univentionObjectType": [b"groups/group"],
        "cn": [b"old-name"],
    }

    new_ldap_obj = {
        "entryUUID": [b"test-uuid-789"],
        "entryDN": [b"cn=modified-group,cn=groups,dc=example,dc=com"],
        "univentionObjectType": [b"groups/group"],
        "cn": [b"new-name"],
    }

    mock_cache.retrieve.return_value = {}

    old_udm_obj = {
        "dn": "cn=modified-group,cn=groups,dc=example,dc=com",
        "uuid": "test-uuid-789",
        "objectType": "groups/group",
        "properties": {"name": "old-name"},
    }

    new_udm_obj = {
        "dn": "cn=modified-group,cn=groups,dc=example,dc=com",
        "uuid": "test-uuid-789",
        "objectType": "groups/group",
        "properties": {"name": "new-name"},
    }

    mock_ldap2udm.ldap_to_udm.side_effect = [old_udm_obj, new_udm_obj]

    ts = datetime.datetime(2024, 1, 1, 12, 0, 0)

    await transformer_service.handle_change(new_ldap_obj, old_ldap_obj, ts)

    assert mock_event_sender.send_event.call_count == 1
    sent_message = mock_event_sender.send_event.call_args[0][0]

    assert sent_message.body.old == old_udm_obj
    assert sent_message.body.new == new_udm_obj
