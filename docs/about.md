## Summary

The provisioning component aims to send information from the leading LDAP
directory to 3rd-party services.

As example, user and group information will be sent to components like OpenXchange
or NextCloud.

## Components

The project comprises three components:

- The main service, "dispatcher", provides an API for publishers and subscribers.
  - Publishers (e.g. the UDM REST server) can connect and publish messages about created, changed, and deleted users.
  - Subscribers (e.g. the OpenXchange connector) can subscribe to certain topics and stay informed about changes.

- A "core" library provides tools shared by publishers and subscribers alike (mostly data models).

- An example client serves as a template for new consumer applications.

## Persistency

Data is persisted in a NATS server.

## Filtering

Each publishing service works in a "realm",
e.g. `udm`.
Inside the realm, it can offer several "topics",
e.g. `users/user`, `groups/group`, and `portal/entries`.

A subscriber needs to state to which combination
of realm and topics it wants to listen.
The dispatcher is responsible for forwarding
only the desired subset of messages to the subscriber.

The subscriber may express its interest using regular expressions,
e.g. `users/.*`.

> TODO: In the future, the subscribers may be able to further
> narrow down the entries, e.g. by providing an LDAP position,
> or filter by UDM, LDAP, or general message properties.

## Authentication / Authorization

None.

> TODO: In the future, the dispatcher is responsible to authenticate
> publishers and subscribers.
> Publishers may only publish messages pertaining to their assigned realm(s).
> Subscribers may only listen to messages from the realms and topics that
> they are permitted to receive.
> In addition, the message content may be censored depending on the subscriber
> (e.g. to strip password hashes from the messages).

> TODO: Maybe it is possible to leverage the Guardian project here?

## Queuing

There is a queue for each registered subscriber.
The queues are implemented using [NATS JetStream](https://docs.nats.io/nats-concepts/jetstream).
See the `queue-configuration` section for details about the NATS configuration.

Each item in the queue has a timestamp.
Messages are requested by the subscribers one by one,
starting with the earliest item available.

A subscriber must acknowledge the successful processing of a message,
Until a message is acknowledged,
the Provisioning API will redeliver the current message when asking for the next message.

See the `prefill` section for further details.

## Parallelization

As little as possible to avoid race conditions:
- Ideally, only one single-threaded, synchronous, instance of the UDM REST API should be used, but in practice that may be too slow. The UDM REST API should deliver messages to the provisioning dispatcher in chronological order. It has to ensure that for one UDM request the order of all corresponding LDAP changes is maintained.
- Use only one subscriber per queue.
- Multiple provisioning dispatcher services may be possible but have not been tested.
