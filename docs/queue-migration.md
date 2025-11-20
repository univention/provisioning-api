# NATS Stream Migration

## Overview

This document describes the NATS stream migration mechanism implemented in the Nubus Provisioning system to support running multiple dispatcher instances in parallel (e.g., on UCS primary and backup nodes).

## Background

The `incoming` stream (from UDM Transformer to Dispatcher) was initially created with `WorkQueue` retention policy, which only delivers each message to one subscriber. To support multiple dispatcher instances that all need to receive the same messages, the stream must use `Interest` retention policy instead.

However, NATS does not allow changing the retention policy of an existing stream on-the-fly. This requires a migration strategy.

## Migration Strategy

The migration follows these steps:

1. **Seal the stream**: The existing stream is marked as "sealed", preventing new messages from being published to it
2. **Drain the stream**: All messages in the sealed stream are processed normally by consumers
3. **Delete and recreate**: Once empty, the sealed stream is deleted and recreated with the new configuration

This ensures **no message loss** during the migration.

## Implementation

### IncomingQueue Configuration

The `IncomingQueue` class now uses `INTEREST` retention policy by default:

```python
class IncomingQueue(BaseQueue):
    retention_policy = RetentionPolicy.INTEREST
    deliver_policy = DeliverPolicy.NEW
```

### Automatic Migration

The Dispatcher service automatically handles migration when started:

```python
status = await self.mq_pull.initialize_subscription(queue_type, migrate_stream=True)
```

#### Migration Flow

1. **Stream doesn't exist**: Creates new stream with INTEREST mode → returns `QueueStatus.READY`

2. **Stream exists with correct config**: Updates stream → returns `QueueStatus.READY`

3. **Stream exists with incorrect config** (e.g., WorkQueue mode):
   - If `migrate_stream=False`: Raises `ServerError`
   - If `migrate_stream=True`: Initiates migration process

4. **Migration process**:
   - Seals the existing stream (idempotent operation)
   - Checks message count:
     - If messages > 0: Returns `QueueStatus.SEALED_FOR_MIGRATION`
     - If messages == 0: Deletes old stream, creates new one, returns `QueueStatus.READY`

5. **Dispatcher behavior**:
   - If status is `READY`: Processes messages normally
   - If status is `SEALED_FOR_MIGRATION`: Continues draining messages from sealed stream
   - On each Empty timeout: Attempts to complete migration
   - Once stream is empty: Migration completes automatically

### Migration States

The `QueueStatus` enum defines two states:

- `READY`: Stream is ready for normal operations
- `SEALED_FOR_MIGRATION`: Stream is sealed and waiting to be drained

## Deployment Scenarios

### New Installation

No migration needed. The `incoming` stream is created with `INTEREST` mode from the start.

### Upgrade from Old Version

When upgrading from a version using `WorkQueue` mode:

1. Deploy new version of Dispatcher
2. Dispatcher detects retention policy mismatch
3. Dispatcher seals the old stream
4. Dispatcher continues processing existing messages
5. Once all messages are processed, Dispatcher automatically:
   - Deletes the old stream
   - Creates new stream with INTEREST mode
   - Resumes normal operation

### Multiple Dispatcher Instances

When multiple dispatcher instances are running (e.g., UCS primary + backup):

- Only one instance will seal the stream (first one to detect the mismatch)
- All instances can continue draining the sealed stream
- Once empty, any instance can complete the migration
- Sealing is idempotent - safe to call multiple times
- After migration, all instances receive all messages (INTEREST mode)

## Monitoring

### Log Messages

The migration process logs the following messages:

```
INFO: Stream 'stream:incoming' sealed for migration
INFO: Stream 'stream:incoming' sealed with N messages remaining to drain
INFO: Sealed stream 'stream:incoming' is empty, completing migration
INFO: Migration completed for 'stream:incoming'
INFO: Stream migration completed, resuming normal operation
```

### Error Messages

If migration is not enabled but required:

```
ERROR: Stream 'stream:incoming' update failed but migration not enabled. See docs/queue-migration.md. Error: <details>
```

## Manual Intervention

In rare cases where automatic migration fails, operators can manually intervene:

### Check Stream Status

```bash
nats stream info stream:incoming
```

### Force Delete and Recreate (DATA LOSS!)

```bash
# Only do this if you accept losing unprocessed messages!
nats stream delete stream:incoming
# New stream will be created automatically on next dispatcher startup
```

## References

- [Queue Configuration Documentation](./queue_configuration.md): General queue configuration details
- [UCS Architecture](./ucs/architecture.md): UCS-specific provisioning architecture
