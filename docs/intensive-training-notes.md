# Intensive training speaker notes on the Nubus Provisioning stack

## Summit slides
- Where we are coming from
- Architecture
- Don't go to the HTTP rest calls yet.

## Quick excursion into the docs
- https://docs.software-univention.de/nubus-kubernetes-architecture/latest/en/components/provisioning-service.html#component-provisioning-service-consumer-messages-http-rest-api
- https://docs.software-univention.de/nubus-kubernetes-customization/latest/en/api/provisioning.html#customization-api-provisioning-subscription
- Show the components in a Nubus deployment.
	- Kubectl get pods.
	- Show the logs.
## The Provisioning API endpoints
- Continue with the presentation.
- Interact with the API via the swagger UI
	- dev-env username: admin password: provisioning
	- jlohmer-main: username: admin password: supersecret
- Create a new Subscription based on the selfservice subscription.
	- selfervice first with wrong password
	- then with right password
- Recreate the same subscription
	- Same password and everything works
	- changing realms does not work
- Get a message from the subscription.
	**!Different credentials needed!
- Try to get the same message again.
	- First try won't work because of nats timeout (can be fixed later)
	- Second try works. Show updated `num_delivered`
- Acknowledge the message

- Acknowledge the message

- How many more messages are in here?
- Let's have a look at our nats queues
	- credentials: username: admin password: supersecret
	-
- Increase the timeout in the background and modify a user object.
- Show that the message instantly arrived.

- Back to NATS:
- show streams, consumers and kv

## Build the example consumer
Show the example consumer code
- explain why no differentiation between `create` `modify` and `delete`
- Show the logs in the dev-env
