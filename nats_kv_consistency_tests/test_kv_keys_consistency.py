# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Reproduce the dispatcher's "dropped messages" root cause at the NATS layer.

Root cause (see ``dispatcher-dropped-messages-investigation.md``): enumerating a
JetStream KV bucket with ``KeyValue.keys()`` is **not** a consistent snapshot.
It spins up an ephemeral ``last_per_subject`` consumer and decides it has "seen
everything" from the server-reported ``num_pending``. On a 3-node cluster, when
the enumeration is read from a *different* node than the writes went to, that
decision fires too early and the call returns an **empty or partial** key set.
The dispatcher then rebuilt its routing table from that bad view and dropped
live messages.

This suite talks to the real cluster with ``nats-py`` directly -- no
provisioning code involved -- so it isolates the defect to the KV enumeration:

* ``test_reproduce_keys_enumeration_inconsistency`` *hunts* for the bug: it
  drives concurrent create/delete churn and samples ``KeyValue.keys()`` from
  another node until it catches a committed key being dropped. Passing means the
  inconsistency **was reproduced** on this cluster; the same load never broke the
  snapshot read.
* the ``*snapshot*`` tests assert the proposed fix
  (``stream_info(subjects_filter=...)`` + ``get_last_msg``) always returns every
  committed key -- the durable regression tests, expected to pass.

Why the reproduction "hunts" instead of asserting ``keys()`` is always wrong:
the race is probabilistic and far more likely on a busy/cold cluster (52% of
samples on a fresh cluster, ~0.3% on a warm one in our runs). Asserting
"``keys()`` must be correct" would therefore *flakily pass* on a quiet cluster
and falsely read as "bug fixed". Asserting "we observed at least one drop within
a budget" is the robust form of a reproduction.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Callable, List, Set

import pytest
from conftest import ClusterConfig
from kv_enumeration import keys_via_client, keys_via_snapshot
from nats.js import JetStreamContext
from nats.js.kv import KeyValue

pytestmark = pytest.mark.asyncio

# The reproduction race is probabilistic; hunt across a few churn rounds with
# several concurrent writers so it triggers reliably even on a warm cluster.
NUM_WRITERS = 3
MAX_HUNT_ATTEMPTS = 12


def _value() -> bytes:
    return str(uuid.uuid4()).encode()


# --------------------------------------------------------------------------- #
# Scenario A: batched writes, immediate cross-node snapshot enumeration
# --------------------------------------------------------------------------- #


@dataclass
class RoundFailure:
    round: int
    expected: int
    got: int
    missing: List[str]


async def _snapshot_failures_over_batches(
    cluster: ClusterConfig,
    write_kv: KeyValue,
    read_js: JetStreamContext,
    bucket: str,
) -> List[RoundFailure]:
    """Write disjoint batches of keys (acked on the write node) and, right after
    each batch, take a consistent-snapshot enumeration from the read node. An
    acked key is committed, so every snapshot must contain all keys written so
    far. Returns the rounds (if any) where it did not.
    """
    expected: Set[str] = set()
    failures: List[RoundFailure] = []

    for r in range(cluster.rounds):
        for i in range(cluster.keys_per_round):
            key = f"r{r:04d}-k{i:04d}"
            await write_kv.put(key, _value())  # awaited -> committed/acked
            expected.add(key)

        snapshot = await keys_via_snapshot(read_js, bucket)
        if snapshot != expected:
            failures.append(RoundFailure(r, len(expected), len(snapshot), sorted(expected - snapshot)[:10]))

    return failures


async def test_snapshot_enumeration_is_consistent_over_batches(cluster, write_js, read_js, kv_bucket):
    """FIX (durable regression): the consistent-snapshot read returns every
    committed key when read from another cluster node, batch after batch.
    """
    write_kv = await write_js.key_value(kv_bucket)

    failures = await _snapshot_failures_over_batches(cluster, write_kv, read_js, kv_bucket)

    assert not failures, (
        f"cross-node snapshot enumeration was empty or partial in "
        f"{len(failures)}/{cluster.rounds} rounds; examples: "
        + "; ".join(f"round {f.round}: expected {f.expected}, got {f.got}" for f in failures[:5])
    )


# --------------------------------------------------------------------------- #
# Scenario B: concurrent create/delete churn, sampled cross-node enumeration
# --------------------------------------------------------------------------- #
#
# Closer to the dispatcher's real workload: subscriptions are created and
# deleted concurrently (test fixtures) while the enumeration runs.
#
# Invariant used for the assertions: capture the acked-live key set *before* and
# *after* each enumeration and require only their intersection -- the keys that
# stayed live for the whole read. Because key names are unique (never re-added),
# that intersection is exactly the set of continuously-live keys, so a correct
# enumeration must contain all of them. This excludes keys the writer deletes
# mid-read, which would otherwise be false positives.


@dataclass
class ChurnReport:
    samples: int = 0
    violations: List[str] = field(default_factory=list)

    def merge(self, other: "ChurnReport") -> None:
        self.samples += other.samples
        self.violations.extend(other.violations)

    def summary(self, method: str) -> str:
        return (
            f"cross-node {method} enumeration dropped committed keys in "
            f"{len(self.violations)}/{self.samples} samples taken during concurrent churn; "
            f"examples: " + "; ".join(self.violations[:5])
        )


async def _run_churn(
    cluster: ClusterConfig,
    write_kv: KeyValue,
    read_kv: KeyValue,
    read_js: JetStreamContext,
    bucket: str,
    tag: str,
    num_writers: int,
) -> tuple[ChurnReport, ChurnReport]:
    """Drive ``num_writers`` concurrent create/delete writers on the write node
    while continuously sampling both enumeration strategies from the read node.

    ``tag`` namespaces the key names so repeated calls against the same bucket
    never collide (keeps the "unique key names" invariant across hunt attempts).
    """
    acked_live: Set[str] = set()  # keys currently put-and-acked and not deleted
    done = asyncio.Event()
    finished_writers = 0
    client_report = ChurnReport()
    snapshot_report = ChurnReport()

    per_writer = max(1, (cluster.rounds * cluster.keys_per_round) // num_writers)

    async def writer(w: int) -> None:
        nonlocal finished_writers
        created: List[str] = []
        for n in range(per_writer):
            key = f"{tag}-w{w}-k{n:05d}"
            await write_kv.put(key, _value())
            acked_live.add(key)
            created.append(key)
            # Delete roughly every 4th key once this writer has a backlog, to
            # mint tombstones like the subscription create/delete churn.
            if n % 4 == 3 and len(created) > 8:
                victim = created.pop(0)
                await write_kv.delete(victim)
                acked_live.discard(victim)
        finished_writers += 1
        if finished_writers == num_writers:
            done.set()

    async def sampler(report: ChurnReport, enumerate_fn: Callable) -> None:
        while not done.is_set():
            before = set(acked_live)
            result = await enumerate_fn()
            after = set(acked_live)
            report.samples += 1
            stable = before & after  # continuously live -> must be enumerable
            missing = stable - result
            if missing:
                report.violations.append(
                    f"missing {len(missing)} continuously-live keys "
                    f"(e.g. {sorted(missing)[:5]}), result size {len(result)}"
                )
            await asyncio.sleep(0)  # yield to the writers

    await asyncio.gather(
        *(writer(w) for w in range(num_writers)),
        sampler(client_report, lambda: keys_via_client(read_kv)),
        sampler(snapshot_report, lambda: keys_via_snapshot(read_js, bucket)),
    )
    return client_report, snapshot_report


async def test_reproduce_keys_enumeration_inconsistency(cluster, write_js, read_js, kv_bucket):
    """REPRODUCTION: cross-node ``KeyValue.keys()`` drops committed keys under
    concurrent churn.

    Hunts across churn rounds until a drop is observed (or the budget is spent).
    Passing == the inconsistency was reproduced on this cluster. The same load,
    read with the consistent snapshot, never dropped a key.
    """
    write_kv = await write_js.key_value(kv_bucket)
    read_kv = await read_js.key_value(kv_bucket)

    client_total = ChurnReport()
    snapshot_total = ChurnReport()
    for attempt in range(MAX_HUNT_ATTEMPTS):
        client_report, snapshot_report = await _run_churn(
            cluster, write_kv, read_kv, read_js, kv_bucket, tag=f"a{attempt}", num_writers=NUM_WRITERS
        )
        client_total.merge(client_report)
        snapshot_total.merge(snapshot_report)
        if client_report.violations:
            break

    assert client_total.samples > 0, "no enumeration samples were taken"
    assert client_total.violations, (
        f"could not reproduce the keys() inconsistency in {MAX_HUNT_ATTEMPTS} churn "
        f"rounds ({client_total.samples} samples). The cluster may be too quiet; "
        f"raise KV_ROUNDS/KV_KEYS_PER_ROUND or run against a busier/colder cluster."
    )
    # The whole point of the fix: under the exact same churn, the snapshot read
    # never dropped a committed key.
    assert not snapshot_total.violations, snapshot_total.summary("snapshot")


async def test_snapshot_enumeration_is_consistent_under_churn(cluster, write_js, read_js, kv_bucket):
    """FIX (durable regression): under concurrent create/delete churn, the
    consistent-snapshot read never drops a continuously-live committed key.
    """
    write_kv = await write_js.key_value(kv_bucket)
    read_kv = await read_js.key_value(kv_bucket)

    _, snapshot_report = await _run_churn(
        cluster, write_kv, read_kv, read_js, kv_bucket, tag="churn", num_writers=NUM_WRITERS
    )

    assert snapshot_report.samples > 0, "no enumeration samples were taken"
    assert not snapshot_report.violations, snapshot_report.summary("snapshot")
