# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Three ways to enumerate the live keys of a JetStream KV bucket.

The whole investigation hinges on the difference between them:

``keys_via_client``
    What ``nats-py`` (and the provisioning ``get_all_subscriptions`` used to)
    do: ``KeyValue.keys()``. Internally spins up an ephemeral
    ``last_per_subject`` consumer and decides "I've seen everything" from the
    server-reported ``num_pending``. On a 3-node cluster, read from a follower
    node under concurrent writes, that decision fires too early and the call
    returns an **empty or partial** set (or raises ``NoKeysError``).

``keys_via_snapshot``
    The recommended fix: enumerate the committed stream state with
    ``stream_info(subjects_filter=...)`` and read each value with
    ``get_last_msg``. Never consults ``num_pending`` -> a consistent
    point-in-time snapshot.

``stream_committed_subjects``
    Ground truth for the assertions: the set of live subjects the leader has
    committed, straight from ``stream_info``. This is what *should* be
    enumerable.
"""

from __future__ import annotations

from typing import Set

from nats.js import JetStreamContext
from nats.js.errors import NoKeysError, NotFoundError
from nats.js.kv import KV_DEL, KV_OP, KV_PURGE, KeyValue


def stream_name(bucket: str) -> str:
    return f"KV_{bucket}"


def subject_prefix(bucket: str) -> str:
    return f"$KV.{bucket}."


async def keys_via_client(kv: KeyValue) -> Set[str]:
    """Stock ``nats-py`` enumeration -- the buggy path under test.

    ``keys()`` raises ``NoKeysError`` when its (possibly premature) caught-up
    decision collected zero keys. The provisioning adapter mapped that to an
    empty list, so we do the same here.
    """
    try:
        return set(await kv.keys())
    except NoKeysError:
        return set()


async def keys_via_snapshot(js: JetStreamContext, bucket: str) -> Set[str]:
    """Consistent-snapshot enumeration -- the proposed fix.

    Key set from committed stream state, values via ``get_last_msg``, skipping
    not-yet-purged tombstones. No ``num_pending`` anywhere.
    """
    stream = stream_name(bucket)
    prefix = subject_prefix(bucket)
    try:
        info = await js.stream_info(stream, subjects_filter=f"{prefix}>")
    except NotFoundError:
        return set()

    subjects = (info.state.subjects or {}) if info.state else {}
    live: Set[str] = set()
    for subject in subjects:
        try:
            msg = await js.get_last_msg(stream, subject)
        except NotFoundError:
            continue
        operation = (msg.headers or {}).get(KV_OP)
        if operation in (KV_DEL, KV_PURGE):
            continue
        live.add(subject[len(prefix) :])
    return live


async def stream_committed_subjects(js: JetStreamContext, bucket: str) -> Set[str]:
    """Ground-truth live key set from the committed stream state.

    Identical key-set computation to ``keys_via_snapshot`` but read against the
    node this ``js`` is connected to; used by tests to assert what *should* have
    been enumerable at the moment of the read.
    """
    return await keys_via_snapshot(js, bucket)
