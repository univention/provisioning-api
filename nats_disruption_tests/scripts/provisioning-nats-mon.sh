#!/bin/bash
docker run --network host -i --rm natsio/nats-box sh -c "watch -n .5 'nats --user admin --password univention stream ls; nats --user admin --password univention kv ls SUBSCRIPTIONS'"; 