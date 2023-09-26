Prefilling
==========

When a new subscriber registers with the provisioning service,
it can request to be informed about the current state of objects
in the LDAP.

This is accomplished by setting `"fill_queue": true` in the
subscription request.

Requirements
------------

The initial state should be served first,
before the "live" changes are served to the subscriber.

The initial state should be served in the order that is requested,
e.g. when the subscription lists "groups" and "users",
the initial groups should be provided ahead of the initial users.

The initialization may take quite some time in large installations.
If it fails, it should be possible to restart it safely
without confusing the consumers.

Process
-------

Upon registering a new subscriber,
the queue status is set to "pending".

(If no pre-filling is requested,
the queue status is set to "ok" and the process ends here.)

A background task is started.
It looks at the list of requested topics.

From the corresponding realm UDM REST API
the list of available modules/object types is requested
and filtered for those matching the requested topic.
(If the subscriber's topics contain regular expressions, those are taken into account).

A list of objects is requested from the corresponding UDM module.

The full representation is fetched from the UDM REST API
in a dedicated request for each object.

Then, the object's information is placed in the queue
at timestamp `0`
(i.e. before any "live" messages)
with an auto-incrementing sequence number `X` assigned by Redis
(such that the full message id is `0-X`).

Once the all objects for all object types have been placed in the queue,
the queue status is set to "ok".
Should the pre-filling process terminate prematurely due to an error condition,
the queue status is set to "failed".

Only once the queue status is "ok",
the subscriber will start to receive messages.
This ensures that in case of failures
the queue can be safely cleaned and reinitialized.
