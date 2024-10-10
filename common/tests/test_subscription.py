# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from univention.provisioning.models.subscription import FillQueueStatus, RealmTopic, Subscription


def test_subscription_eq():
    sub1 = Subscription(
        name="foo",
        realms_topics=[RealmTopic(realm="r1", topic="t1"), RealmTopic(realm="r2", topic="t2")],
        request_prefill=True,
        prefill_queue_status=FillQueueStatus.done,
    )
    sub2 = Subscription(
        name="foo",
        realms_topics=[RealmTopic(realm="r2", topic="t2"), RealmTopic(realm="r1", topic="t1")],
        request_prefill=True,
        prefill_queue_status=FillQueueStatus.done,
    )
    assert sub1 == sub2

    sub2.name = "bar"
    assert sub1 != sub2

    sub2.name = "foo"
    assert sub1 == sub2
    rt = sub2.realms_topics.pop()
    assert sub1 != sub2

    sub2.realms_topics.append(rt)
    assert sub1 == sub2
    sub2.request_prefill = False
    assert sub1 != sub2

    sub2.request_prefill = True
    assert sub1 == sub2
    sub2.prefill_queue_status = FillQueueStatus.pending
    assert sub1 != sub2


def test_subscription_hash():
    sub1 = Subscription(
        name="foo",
        realms_topics=[RealmTopic(realm="r1", topic="t1"), RealmTopic(realm="r2", topic="t2")],
        request_prefill=True,
        prefill_queue_status=FillQueueStatus.done,
    )
    sub2 = Subscription(
        name="bar",
        realms_topics=[RealmTopic(realm="r3", topic="t3")],
        request_prefill=False,
        prefill_queue_status=FillQueueStatus.done,
    )
    subs = {sub1, sub2}

    assert sub1 in subs
    assert sub2 in subs
