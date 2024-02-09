# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
import requests

from tests.conftest import REALM, TOPIC
from univention.admin.rest.client import UDM


def create_message_via_events_api(provisioning_base_url: str):
    payload = {
        "publisher_name": "consumer_client_tests",
        "ts": "2024-02-07T09:01:33.835Z",
        "realm": REALM,
        "topic": TOPIC,
        "body": {"foo": "bar"},
    }

    response = requests.post(f"{provisioning_base_url}events/v1/events", json=payload)

    print(response.json())
    assert response.status_code == 202, "Failed to post message to queue"


def create_message_via_udm_rest_api(udm: UDM):
    groups = udm.get(TOPIC)
    assert groups
    group = groups.new()
    group.properties["name"] = str(uuid.uuid1())
    group.save()

    return group
