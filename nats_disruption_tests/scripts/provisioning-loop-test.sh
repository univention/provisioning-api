#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


while true ; do
    date
    pytest -vv  tests/test_workflow.py::test_prefill_with_multiple_topics \
                tests/test_consumer_client.py::test_get_multiple_messages ;
    [ "$1" == "no-cleanup" ] && continue
    docker run --network host -i --rm natsio/nats-box sh -c "
        nats --user admin --password univention kv ls SUBSCRIPTIONS  \
            | xargs -i nats --user admin --password univention  kv del -f SUBSCRIPTIONS {} ; \
        nats stream ls --user admin --password univention \
            | grep stream \
            | sed -re 's/.*(stream[:a-z0-9-]+).*/\1/' \
            | grep -E '[0-9]'  \
            | xargs -i nats --user admin --password univention stream del -f {};";
    sleep 3
done | tee ../provisioning-loop-test.log

