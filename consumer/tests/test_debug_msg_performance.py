# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import random
import time
from datetime import datetime

import pytest

from univention.provisioning.consumer.api import MessageHandler
from univention.provisioning.models.message import Body, Message


@pytest.fixture
def large_group_message():
    users = [f"uid=user{i},cn=users,dc=example,dc=com" for i in range(10000)]
    random.shuffle(users)
    old_body = {
        "dn": "cn=testgroup,cn=groups,dc=example,dc=com",
        "objectType": "groups/group",
        "properties": {
            "name": "testgroup",
            "users": users[:],
        },
    }
    new_users = users[:] + ["uid=newuser,cn=users,dc=example,dc=com"]
    random.shuffle(new_users)
    new_body = {
        "dn": "cn=testgroup,cn=groups,dc=example,dc=com",
        "objectType": "groups/group",
        "properties": {
            "name": "testgroup",
            "users": new_users,
        },
    }
    return Message(
        realm="udm",
        topic="groups/group",
        publisher_name="udm-listener",
        ts=datetime.now(),
        body=Body(old=old_body, new=new_body),
    )


@pytest.fixture
def small_group_message():
    users = ["uid=user1,cn=users,dc=example,dc=com", "uid=user2,cn=users,dc=example,dc=com"]
    random.shuffle(users)
    old_body = {
        "dn": "cn=testgroup,cn=groups,dc=example,dc=com",
        "objectType": "groups/group",
        "properties": {
            "name": "testgroup",
            "users": [users[0]],
        },
    }
    new_body = {
        "dn": "cn=testgroup,cn=groups,dc=example,dc=com",
        "objectType": "groups/group",
        "properties": {
            "name": "testgroup",
            "users": users[:],
        },
    }
    return Message(
        realm="udm",
        topic="groups/group",
        publisher_name="udm-listener",
        ts=datetime.now(),
        body=Body(old=old_body, new=new_body),
    )


def test_debug_msg_performance_large_group(large_group_message):
    t0 = time.perf_counter()
    result = MessageHandler.debug_msg(large_group_message)
    elapsed = time.perf_counter() - t0
    assert "realm: 'udm'" in result
    assert "topic: 'groups/group'" in result
    assert "action: update" in result
    assert elapsed < 1.0, f"debug_msg took {elapsed:.3f}s for 10000-user group, expected < 1s"


def test_debug_msg_performance_small_group(small_group_message):
    t0 = time.perf_counter()
    result = MessageHandler.debug_msg(small_group_message)
    elapsed = time.perf_counter() - t0
    assert "realm: 'udm'" in result
    assert "topic: 'groups/group'" in result
    assert "action: update" in result
    assert elapsed < 0.1, f"debug_msg took {elapsed:.3f}s for 2-user group, expected < 0.1s"


def test_debug_msg_preserves_message_integrity(large_group_message):
    original_old_users = large_group_message.body.old["properties"]["users"][:]
    original_new_users = large_group_message.body.new["properties"]["users"][:]

    MessageHandler.debug_msg(large_group_message)

    assert large_group_message.body.old["properties"]["users"] == original_old_users
    assert large_group_message.body.new["properties"]["users"] == original_new_users


def test_debug_msg_group_user_diff(small_group_message):
    result = MessageHandler.debug_msg(small_group_message)
    assert "uid=user2,cn=users,dc=example,dc=com" in result or "'users'" in result
