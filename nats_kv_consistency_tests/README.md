<!--
SPDX-License-Identifier: AGPL-3.0-only
SPDX-FileCopyrightText: 2026 Univention GmbH
-->

# NATS KV cross-node consistency reproduction

A **standalone** pytest suite that reproduces, directly against a real 3-node
JetStream cluster with `nats-py`, the root cause behind the dispatcher's
"dropped messages" bug (see `../dispatcher-dropped-messages-investigation.md`).

It imports **no provisioning code** — it is pure NATS client/server behaviour —
so it isolates the defect to the KV enumeration itself.

## What it shows

`KeyValue.keys()` is not a consistent snapshot: it enumerates via an ephemeral
`last_per_subject` consumer and decides it is "caught up" from the server's
`num_pending`. When the enumeration is read from a **different cluster node**
than the writes went to, that decision fires too early and the call returns an
**empty or partial** key set — exactly what wiped the dispatcher's routing map.

| Test | What it does | Green means |
| --- | --- | --- |
| `test_reproduce_keys_enumeration_inconsistency` | drives concurrent create/delete churn and **hunts** for `KeyValue.keys()` (read from another node) dropping a committed key | the inconsistency **was reproduced** on this cluster |
| `test_snapshot_enumeration_is_consistent_over_batches` | `stream_info(subjects_filter=…)` + `get_last_msg`, batch after batch | the fix returns every committed key |
| `test_snapshot_enumeration_is_consistent_under_churn` | same snapshot read under the same concurrent churn | the fix never drops a key |

The reproduction test asserts both halves of the story on one run: `keys()`
dropped a committed key, and the **same** load read with the consistent snapshot
did not — pinning the defect to the `keys()` enumeration alone.

### Why the reproduction "hunts" instead of asserting `keys()` is always wrong

The race is probabilistic and depends heavily on cluster load: in our runs it hit
~52% of samples on a fresh/busy cluster but only ~2–5% on a warm, idle one.
Asserting "`keys()` must be correct" would therefore **flakily pass** on a quiet
cluster and be misread as "bug fixed". Asserting "we observed at least one drop
within a budget" (up to `MAX_HUNT_ATTEMPTS` churn rounds of `NUM_WRITERS`
concurrent writers) is the robust form of a reproduction. If it cannot reproduce
within the budget it fails with a hint to raise the load or use a busier cluster.

The correctness invariant is drop-safe: a key only counts as "must be
enumerable" if it stayed live **before and after** the read (continuously live),
so keys the writer deletes mid-read are never counted as false drops.

## The write-node ≠ read-node design

The reproduction depends on writes and reads landing on **different** nodes, so
the two endpoints are configured independently and each connection is pinned to
its node (`allow_reconnect=False, dont_randomize=True`):

| env var | default (compose network) | host-side (published ports) |
| --- | --- | --- |
| `KV_WRITE_URL` | `nats://nats1:4222` | `nats://localhost:4222` (nats1) |
| `KV_READ_URL` | `nats://nats3:4222` | `nats://localhost:4223` (nats3) |
| `KV_USER` / `KV_PASSWORD` | `admin` / `univention` | same |
| `KV_REPLICAS` | `3` | `3` |
| `KV_ROUNDS` | `40` | `40` |
| `KV_KEYS_PER_ROUND` | `25` | `25` |

If neither endpoint is reachable the whole suite **skips** (never fails), so it
is safe to collect anywhere.

## Running

Dependencies: `nats-py>=2.14`, `pytest`, `pytest-asyncio` (verified against
`nats-py 2.15.0`, which still carries the bug).

Inside the compose network (a container on the same network as `nats1/2/3` —
defaults to writing to `nats1`, reading from `nats3`):

```sh
uv run --no-project \
  --with "nats-py>=2.14,<3" --with pytest --with "pytest-asyncio>=0.25" \
  pytest nats_kv_consistency_tests -v
```

From the host, against the compose-published ports (`nats1`→4222, `nats3`→4223):

```sh
KV_WRITE_URL=nats://localhost:4222 KV_READ_URL=nats://localhost:4223 \
uv run --no-project \
  --with "nats-py>=2.14,<3" --with pytest --with "pytest-asyncio>=0.25" \
  pytest nats_kv_consistency_tests -v
```

(If the deps are already on your `PATH`, plain `pytest nats_kv_consistency_tests -v` works too.)

Turn the load up if the race does not trigger on a fast/quiet cluster:

```sh
KV_ROUNDS=100 KV_KEYS_PER_ROUND=50 pytest nats_kv_consistency_tests -v
```
