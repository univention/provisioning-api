## Overview

Nearly all communication between the different Nubus Provisioning services is Queue-based.
This is advantageous because the queue persists the event / request
and ensures it's handling with retries if necessary.

In the provisioning stack, there are two types of queues:

**Internal queues** between the different components in the provisioning stack.
E.g. between the LDIF-Producer and the UDM-Transformer.
The components have direct access to these queues.

**Consumer queues** hold all messages
that have not(yet) been processed by a specific Provisioning Consumer.
The Provisioning Consumers have no direct access to NATS.
Instead, they request messages from the Provisioning API,
which acts as a proxy for the Provisioning Consumer NATS Stream.

## Queue creation

Every queue has a provisioning component that writes to it
and a component that reads from it.

Instead orchestrating that the writer or reader starts first
and creates the stream, both sides simply check,
if the Queue already exists and create or update it depending on the answer.
This makes deployment and update scenarios much simple,
but the Queue configuration must be shared between all components.
For this reason, things like the queue names and their configuration details
are included in the Message Queue Adapters.

## Queue configuration

Nats Streams are configured when they are created
and some options can be updated later.

The basic requirement is:
Serverside retries / redeliveries while retaining the message order.

What's the next message can only be decided
when the status of the current message is clear.
If the current message is acknowledged, you get the next message.
If the message is marked for redelivery (negative acknowledgement),
you get the same message again.

This makes it an inherently sequential operation and limits opportunities for parallelization.
But that's a topic for a different section.

### Acknowledge

We request NATS messages with explicit acknowledgements activated.
NATS gives us three acknowledgement options:

`ack()` acknowledge
`nack()` acknowledge_negatively / mark for redelivery.
`ack_wait()` extend the acknowledgement timeout.

Nats requires an acknowledgement timeout.
If nats recieves no acknowledgement (neither `ack` or `nack`)
it eventually assumes that something went wrong
and will itself mark the message for redelivery.
This timeout can be periodically extended.

In addition we can limit the amount of in-flight messages
with the `max_ack_pending` config option.

Explicit acknowledgement in combination with `max_ack_pending=1`
gives us the desired behaviour for (nearly) all internal queues.

This way, we can even have a hot standby for every component.
It's not currently supported but could easily be configured in the future.
We can deploy multiple instances of a component.
They all subscribe to the same queue
and the `max_ack_pending=1` acts like a lock with timeout,
so that all messages are consumed sequentially, preserving the message order.

The consumer queues are proxied by the Provisioning API.
Currently the provisioning API has no option for an acknowledgement timeout
or even for a negative acknowledgement.

Provisioning consumers simply keep getting the same message
until they acknowledge the message.
At which point they get the next message.
This behaviour is required by Provisioning Consumers that rely on the message order.
Like the OX-Connector.
In the future, we should support a second API,
optimized for consumers that don't rely on the message order.
Like the Selfservice-Listener.
This is just a performance improvement and enables parallelization,
and thus not necessary for Nubus 1.0

How does the Provisioning API achieve this Behaviour?

It simply delivers the oldest message from the Consumer NATS Stream.
When the Provisioning Consumer acknowledges a message, it deletes it from the stream.
This makes the Provisioning API simple and stateless, but makes
parallelization or even hot standby of Provisioning Consumers impossible.

### Cleanup of old messages

We don't want to keep messages forever,
but only as long as they are needed by someone.
Messages in Consumer NATS Streams are deleted by the Provisionig API

If a Consumer is deleted, it's NATS Stream is also deleted.

But what about Internal NATS Streams,
there messages are only acknowledged and not deleted.

NATS lets us choose between three retention policies:

**LimitsPolicy** (default)
Define a queue size limit. When that is reached,
either the oldest or newest messages are deleted. (configurable)
**This can lead to lost messages and is not suitable**

**InterestPolicy**
A message is only kept until all consumers have acknowledged it.
This sounds good, but is dangerous.
If messages are added to the stream before a consumer is configured,
**the message gets lost**. It may work but is tricky to implement.

**WorkQueuePolicy**
A message is deleted once it has been acknowledged once.
A limitation is that only one Consumer can be created for the stream.
This limitation is fine for us.

InterestPolicy could work, but WorkQueuePolicy is the safer option.

## Needed configuration

### Internal NATS Streams

- Explicit acknowledgement with timeout
- max_ack_pending = 1
- RetentionPolicy = WorkQueuePolicy
- All stream size limits are disabled. (set to infinite)

### Provisioning Consumer NATS streams
- no acknowledgement
- RetentionPolicy = LimitsPolicy (default)
- All stream size limits are disabled. (set to infinite)

### Exception: Prefill trigger stream

Here, we don't need max_ack_pending = 1
which would allow multiple prefill pods
to work on multiple prefill events concurrently.
Not necessary for Nubus 1.0.
