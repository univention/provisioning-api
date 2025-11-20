# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, Mock

import pytest
from nats.js.api import RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError, ServerError
from test_helpers.mock_data import SUBSCRIPTION_NAME

from univention.provisioning.backends.message_queue import QueueStatus
from univention.provisioning.backends.nats_mq import IncomingQueue


@pytest.mark.anyio
class TestNatsMQMigration:
    """Tests for NATS stream migration functionality."""

    incoming_queue = IncomingQueue(SUBSCRIPTION_NAME)

    async def test_ensure_stream_creates_new_stream(self, mock_nats_mq_adapter):
        """Test that ensure_stream creates a new stream if it doesn't exist."""
        mock_nats_mq_adapter._js.stream_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter._js.add_stream = AsyncMock()

        status = await mock_nats_mq_adapter.ensure_stream(self.incoming_queue)

        mock_nats_mq_adapter._js.add_stream.assert_called_once_with(self.incoming_queue.stream_config())
        assert status == QueueStatus.READY

    async def test_ensure_stream_updates_existing_stream_success(self, mock_nats_mq_adapter):
        """Test that ensure_stream updates an existing stream successfully."""
        mock_stream_info = Mock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_stream_info)
        mock_nats_mq_adapter._js.update_stream = AsyncMock()

        status = await mock_nats_mq_adapter.ensure_stream(self.incoming_queue)

        mock_nats_mq_adapter._js.update_stream.assert_called_once_with(self.incoming_queue.stream_config())
        assert status == QueueStatus.READY

    async def test_ensure_stream_update_fails_no_migration(self, mock_nats_mq_adapter):
        """Test that ensure_stream raises error when update fails and migration is not enabled."""
        mock_stream_info = Mock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_stream_info)
        mock_nats_mq_adapter._js.update_stream = AsyncMock(
            side_effect=ServerError(description="Cannot update retention policy")
        )

        with pytest.raises(ServerError):
            await mock_nats_mq_adapter.ensure_stream(self.incoming_queue, migrate_stream=False)

    async def test_ensure_stream_triggers_migration_on_update_failure(self, mock_nats_mq_adapter):
        """Test that ensure_stream triggers migration when update fails and migration is enabled."""
        mock_stream_info = Mock()
        mock_stream_info.config = StreamConfig(
            name=self.incoming_queue.queue_name,
            subjects=[self.incoming_queue.message_subject],
            retention=RetentionPolicy.WORK_QUEUE,
        )
        mock_stream_info.state = Mock()
        mock_stream_info.state.messages = 0

        mock_nats_mq_adapter._js.stream_info = AsyncMock(side_effect=[mock_stream_info, mock_stream_info])
        mock_nats_mq_adapter._js.update_stream = AsyncMock(
            side_effect=[ServerError(description="Cannot update retention policy"), None]
        )
        mock_nats_mq_adapter._js.delete_stream = AsyncMock()
        mock_nats_mq_adapter._js.add_stream = AsyncMock()

        status = await mock_nats_mq_adapter.ensure_stream(self.incoming_queue, migrate_stream=True)

        # Verify migration was triggered
        assert mock_nats_mq_adapter._js.delete_stream.called
        assert mock_nats_mq_adapter._js.add_stream.called
        assert status == QueueStatus.READY

    async def test_migrate_stream_seals_stream_with_messages(self, mock_nats_mq_adapter):
        """Test that migrate_stream seals a stream that has messages remaining."""
        mock_existing_stream = Mock()
        mock_existing_stream.config = StreamConfig(
            name=self.incoming_queue.queue_name,
            subjects=[self.incoming_queue.message_subject],
            retention=RetentionPolicy.WORK_QUEUE,
        )

        mock_sealed_stream_info = Mock()
        mock_sealed_stream_info.state = Mock()
        mock_sealed_stream_info.state.messages = 5  # Stream has messages

        mock_nats_mq_adapter._js.update_stream = AsyncMock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_sealed_stream_info)

        status = await mock_nats_mq_adapter.migrate_stream(self.incoming_queue, mock_existing_stream)

        # Verify stream was sealed
        assert mock_nats_mq_adapter._js.update_stream.called
        sealed_config = mock_nats_mq_adapter._js.update_stream.call_args[0][0]
        assert sealed_config.sealed is True

        # Verify migration is pending
        assert status == QueueStatus.SEALED_FOR_MIGRATION

    async def test_migrate_stream_completes_when_empty(self, mock_nats_mq_adapter):
        """Test that migrate_stream completes migration when stream is empty."""
        mock_existing_stream = Mock()
        mock_existing_stream.config = StreamConfig(
            name=self.incoming_queue.queue_name,
            subjects=[self.incoming_queue.message_subject],
            retention=RetentionPolicy.WORK_QUEUE,
        )

        mock_sealed_stream_info = Mock()
        mock_sealed_stream_info.state = Mock()
        mock_sealed_stream_info.state.messages = 0  # Stream is empty

        mock_nats_mq_adapter._js.update_stream = AsyncMock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_sealed_stream_info)
        mock_nats_mq_adapter._js.delete_stream = AsyncMock()
        mock_nats_mq_adapter._js.add_stream = AsyncMock()

        status = await mock_nats_mq_adapter.migrate_stream(self.incoming_queue, mock_existing_stream)

        # Verify stream was sealed
        assert mock_nats_mq_adapter._js.update_stream.called

        # Verify migration completed
        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(self.incoming_queue.queue_name)
        mock_nats_mq_adapter._js.add_stream.assert_called_once_with(self.incoming_queue.stream_config())
        assert status == QueueStatus.READY

    async def test_initialize_subscription_returns_status(self, mock_nats_mq_adapter):
        """Test that initialize_subscription returns the correct status."""
        mock_stream_info = Mock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_stream_info)
        mock_nats_mq_adapter._js.update_stream = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter._js.add_consumer = AsyncMock()
        mock_nats_mq_adapter._js.pull_subscribe = AsyncMock()

        status = await mock_nats_mq_adapter.initialize_subscription(self.incoming_queue, migrate_stream=False)

        assert status == QueueStatus.READY

    async def test_incoming_queue_uses_interest_retention(self):
        """Test that IncomingQueue is configured with INTEREST retention policy."""
        queue = IncomingQueue("test-consumer")

        assert queue.retention_policy == RetentionPolicy.INTEREST
        assert queue.name == "incoming"
        assert queue._consumer_name == "test-consumer"

    async def test_migrate_stream_is_idempotent(self, mock_nats_mq_adapter):
        """Test that sealing a stream multiple times is safe (idempotent)."""
        mock_existing_stream = Mock()
        mock_existing_stream.config = StreamConfig(
            name=self.incoming_queue.queue_name,
            subjects=[self.incoming_queue.message_subject],
            retention=RetentionPolicy.WORK_QUEUE,
            sealed=False,
        )

        mock_sealed_stream_info = Mock()
        mock_sealed_stream_info.state = Mock()
        mock_sealed_stream_info.state.messages = 0

        mock_nats_mq_adapter._js.update_stream = AsyncMock()
        mock_nats_mq_adapter._js.stream_info = AsyncMock(return_value=mock_sealed_stream_info)
        mock_nats_mq_adapter._js.delete_stream = AsyncMock()
        mock_nats_mq_adapter._js.add_stream = AsyncMock()

        # First migration
        status1 = await mock_nats_mq_adapter.migrate_stream(self.incoming_queue, mock_existing_stream)

        # Simulate calling migration again (e.g., multiple dispatcher instances)
        mock_existing_stream.config.sealed = True
        status2 = await mock_nats_mq_adapter.migrate_stream(self.incoming_queue, mock_existing_stream)

        assert status1 == QueueStatus.READY
        assert status2 == QueueStatus.READY
