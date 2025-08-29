#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

docker run --network host -i --rm natsio/nats-box sh -c "watch -n .5 'nats --user admin --password univention stream ls; nats --user admin --password univention kv ls SUBSCRIPTIONS'";