<!--
SPDX-License-Identifier: AGPL-3.0-only
SPDX-FileCopyrightText: 2026 Univention GmbH
-->

# Dispatcher drops messages: subscription-mapping rebuild reads an inconsistent KV snapshot

**Status:** root cause found, reliably reproduced in a unit test, fix proposed (not yet implemented).
**Date:** 2026-07-11
**Component:** `provisioning-dispatcher`

---

## TL;DR

The dispatcher silently drops messages whenever a subscription-mapping rebuild
reads an **empty or partial** view of the `SUBSCRIPTIONS` KV bucket and then
**unconditionally replaces** its in-memory routing table with that bad view.

- The rebuild itself is fast (~15 ms) and the *strategy* (full rebuild) is fine.
- The problem is the **read**: `KeyValue.keys()` in the NATS Python client is not a
  consistent snapshot — it spins up an ephemeral `last_per_subject` consumer and
  decides "I've seen everything" from the server's `num_pending`, which is wrong
  under concurrent writes on a **3-node JetStream cluster**.
- Result observed in the e2e runs: **~40 % of rebuilds produced an empty map**
  (`Subscriptions mapping updated: {}`) and **140–169 messages/run were dropped**
  (`No consumers for message ...`). That is the source of the "flaky e2e" failures.
- This is an application-level bug in the dispatcher (message loss under
  subscription churn), not merely test flakiness, and it is **independent of the
  CI runner** (same rate on `dae-s`/`dae-m`/`dae-l`/`dae-xl`).

**Recommended fix:** keep the full rebuild, but enumerate the bucket with a
consistent, `num_pending`-free read — `stream_info(subjects_filter=...)` for the
key set + a direct `get_last_msg` per key — in the existing `nats-py` adapter.
No new dependencies.

---

## 1. Symptom

During the e2e benchmark runs on the new `dae-*` runners, `test-end-to-end`
failed intermittently, with a *different* test failing almost every run and the
compose stack (pull / `up`) always succeeding. Failures observed across 12 failed
jobs, grouped by signature:

| Signature | Count | pytest type | Which tests |
| --- | --- | --- | --- |
| `TimeoutError: Dispatcher did not start routing to subscription '<uuid>' within 30s` | 8 | setup ERROR | varies every run |
| `Failed: Timeout (>10.0s) from pytest-timeout` | 4 | ERROR | `test_get_one_message`, `test_get_multiple_messages` |
| `test_workflow — TypeError: 'NoneType' object is not subscriptable` | 3 | FAILED | always `test_workflow` |
| `500 Internal Server Error` on `POST /v1/subscriptions/…` | 1 | ERROR | one-off |

The "random victim test" pattern is the classic fingerprint of a flaky race, and
15 of 16 events share one root cause.

## 2. Evidence from the dispatcher logs

Downloaded `dispatcher.log` artifacts from three jobs that failed with *different*
symptoms and correlated by timestamp / subscription UUID.

Per job (all three consistent):

| Job (flavor) | `mapping updated` events | empty `{}` | `No consumers` drops |
| --- | --- | --- | --- |
| 2860373 (dae-s) | 57 | 25 | 169 |
| 2860376 (dae-xl) | 57 | 22 | 165 |
| 2860396 (dae-xl) | 57 | 24 | 141 |

Key findings:

- The failing subscription UUIDs (e.g. `35974380-…`) **never appear** in any
  `Subscriptions mapping updated: …` line — the dispatcher never learned about them.
- The map **flaps**: it holds at most 2–3 subscriptions and repeatedly collapses to
  `{}`. An empty rebuild has **zero** `Processing subscription:` lines between
  `Updating subscriptions mapping...` and `Subscriptions mapping updated: {}` — i.e.
  the enumeration returned nothing.
- While the map is empty/partial, published messages hit
  `Found subscriptions: []` → `No consumers for message ...` and are dropped.
- Precise correlation for `test_workflow` (job 2860396): the test failed at
  19:06:56; the dispatcher logged **17 `groups/group` drops** — the udm-listener
  group event the test waited for was dropped, so `GET /next?pop=true` returned
  HTTP 200 with a `null` body → `message["realm"]` on `None` → `TypeError`.

All three symptoms are the same event seen from different angles: a message
published while the routing map did not contain its (still-existing) subscription.

## 3. Root-cause chain

### 3.1 Dispatcher replaces the map unconditionally

`dispatcher/src/univention/provisioning/dispatcher/service.py:112`

```python
async def update_subscriptions_mapping(self, *args, **kwargs) -> None:
    logger.info("Updating subscriptions mapping...")
    new_subscriptions_mapping = {}
    async for sub in self.subscriptions_db.get_all_subscriptions():   # <-- the read
        logger.debug("Processing subscription: %r", sub.name)
        if not await self.mq_push.stream_exists(ConsumerQueue(sub.name)):
            continue
        for realm_topic in sub.realms_topics:
            new_subscriptions_mapping.setdefault(...).setdefault(...).add(sub)
    self._subscriptions = new_subscriptions_mapping                   # <-- unconditional replace (:126)
```

If `get_all_subscriptions()` yields nothing (or a subset), the live map is wiped
(or truncated). `handle_message` then finds no subscription and drops the message
(`service.py:96`, `:110`). The watch callback even receives the changed key +
value, but the method ignores it (`*args, **kwargs`) and does a full re-read.

### 3.2 The read is not a consistent snapshot

`backends/src/univention/provisioning/backends/nats_kv.py:107`

```python
async def get_all_subscriptions(self):
    kv_store = await self._js.key_value(BucketName.subscriptions.value)
    for key in await self.get_keys(BucketName.subscriptions):   # kv_store.keys()
        entry = await kv_store.get(key)
        ...
        yield subscription

async def get_keys(self, bucket):                               # :100
    kv_store = await self._js.key_value(bucket.value)
    try:
        return await kv_store.keys()
    except NoKeysError:
        return []                                               # empty read == "no keys" (:104-105)
```

### 3.3 Why `keys()` returns empty/partial

JetStream KV is **not a key-value database — it's a projection over a stream.** A
bucket `X` is a stream `KV_X`; a key is a subject `$KV.X.<key>`; the value is the
last message on that subject; a delete is a tombstone message. There is **no
server-side "list keys" API** — enumerating keys means replaying the last message
per subject via a consumer.

`nats/js/kv.py` `keys()` therefore:

1. spins up an ephemeral `watchall` consumer (`DeliverPolicy=last_per_subject`,
   meta-only);
2. iterates until a `None` "caught-up" sentinel;
3. raises `NoKeysError` if it collected zero keys.

The "caught-up" decision is made purely from **`num_pending`** — at setup
`if cinfo.num_pending == 0 and received == 0: init_done` and per message
`if meta.num_pending == 0: init_done`. On a **3-node cluster** under concurrent
subscription create/delete (the test fixtures), the freshly-created consumer's
`consumer_info().num_pending` is routinely reported as `0`/low **before** the
last-per-subject backlog is delivered → `keys()` returns empty/partial →
`NoKeysError` → `[]` → the rebuild wipes the map.

In the user's framing: the full rebuild is fine *as long as it is done against a
consistent database version* — and `keys()` does **not** give a consistent version.

## 4. Upstream status (is this known / fixed?)

- **nats-server#4824** — "KV Watch | some keys missing … due to wrong NumPending
  from the server" — CLOSED, labelled `defect`. Confirms the server returns a
  wrong `NumPending` for `last_per_subject` consumers so `Keys()/Watch()` break on
  the nil sentinel early. Filed against server 2.10.0–2.10.5. **We run server 2.14.1**
  (3-node `JetStreamCluster`), and the clustered case still bites.
- **nats.py#842** — "kv.watch/history race can emit initial None too early and
  cause spurious NoKeysError" — CLOSED as COMPLETED (2026-03-24), **no linked fix
  PR**. Body lists **affected version `nats-py 2.14.0` (exactly ours)** and the exact
  code path (post-`subscribe()` `consumer_info()` / `received == 0` race with
  buffered-but-uncounted messages).
- **nats-py latest = 2.15.0** — verified by diffing the 2.15.0 sdist: `watch()`
  changed **only** for TTL/expiry markers (`Nats-Marker-Reason`); the
  `num_pending == 0` caught-up logic and the `received == 0` early-exit are
  **unchanged**. So upgrading the client does **not** fix it.
- **`nats-key-value` (new package, 0.1.0)** — nats-io's ground-up rewrite,
  dependency chain `nats-key-value → nats-jetstream 0.3.0 → nats-core`,
  `requires-python >= 3.13`. Its `get()` uses a reliable direct read
  (`get_last_message_for_subject`), but its `keys()`/`watch()`/`history()` still
  enumerate via an ordered `last_per_subject` consumer terminated by
  **`num_pending == 0`** (`keys()` even early-returns empty when
  `info.num_pending == 0` at creation). Same root vulnerability — **does not fix
  the bug** — and it is a separate, experimental client stack.

## 5. Options considered

1. **Incremental updates from the watch event** (add on put / remove on delete).
   *Rejected:* incremental state can drift and never self-heal; the full rebuild is
   more resilient and consistent.
2. **"Don't overwrite with an empty read".**
   *Rejected:* a genuinely empty bucket is a **valid** state (no subscriptions
   configured ⇒ don't dispatch). A transient-empty and a genuine-empty read are
   indistinguishable at the `get_all_subscriptions()` level, so blanket-ignoring
   empty reads would break the valid case.
3. **Switch the KV adapter to `nats-key-value`.**
   *Rejected:* still `num_pending`-bound (does not fix the bug), pulls in a separate
   0.x client stack alongside `nats-py` (two connections/auth paths, or a full
   messaging-layer rewrite), and requires Python ≥ 3.13. A possible *future*
   platform move once that stack is 1.0 — not a fix for this.
4. **Consistent-snapshot read in the existing `nats-py` adapter.** ✅ Recommended.

## 6. Recommended fix

Keep `update_subscriptions_mapping` as a full rebuild-and-replace. Replace only the
enumeration in `backends/.../nats_kv.py` so it reads a consistent version without
ever consulting `num_pending`:

- **Key set:** `stream_info("KV_SUBSCRIPTIONS", subjects_filter="$KV.SUBSCRIPTIONS.>")`
  → `state.subjects` (subject→count), computed server-side from committed stream
  state. No ephemeral consumer, no caught-up guessing. (Supported in nats-py 2.14,
  `nats/js/manager.py:67`.)
- **Value per key:** `js.get_last_msg("KV_SUBSCRIPTIONS", subject)` (Direct Get of
  last-per-subject — the same reliable primitive `nats-key-value.get()` uses),
  skipping tombstones (latest op = DEL/PURGE).

Properties: consistent point-in-time snapshot; self-healing full rebuild; zero new
dependencies; `update_subscriptions_mapping` untouched; unit-testable at the read
layer. Caveat: `state.subjects` includes not-yet-purged deleted keys, so liveness
is confirmed by the per-key op check.

## 7. Reproduction

Added to `dispatcher/tests/test_dispatcher.py`:

- `test_transient_empty_read_wipes_mapping_and_drops_message` — subscription is
  mapped, a second rebuild reads empty *without a deletion*, and the still-valid
  message is dropped. **Currently FAILS** (`enqueue_message` called 0 times),
  reproducing the bug deterministically (no NATS needed).
- `test_no_subscriptions_configured_does_not_dispatch` — guard: genuinely empty
  bucket ⇒ empty map ⇒ no dispatch. **Passes**, and must keep passing after the fix.

Run from the repo root (redirect the venv so the repo `.venv` is untouched):

```sh
UV_PROJECT_ENVIRONMENT=/tmp/dvenv uv run pytest \
  dispatcher/tests/test_dispatcher.py -p no:cov -o addopts="" -q
# => 1 failed (repro), 2 passed (guard + pre-existing)
```

Note on test placement: with the recommended read-layer fix, the *service-level*
repro asserts a "tolerate empty read" contract the service will not have (full
replace stays). The durable regression test should live at the **read layer**
(assert the enumeration returns the complete set / a consistent snapshot), while
the service keeps its simple full-replace and the guard test above protects the
valid-empty case.

## 8. Environment

- e2e stack: `nats:2.14.1`, 3-node `JetStreamCluster` (nats1/nats2/nats3).
- `nats-py` pinned `>=2.9.0,<3.0.0`; installed **2.14.0**. Latest is **2.15.0**
  (allowed by the pin, but does not fix this).
- dispatcher runs on Python 3.13.

## 9. Key references

Code:
- `dispatcher/src/univention/provisioning/dispatcher/service.py:112` (`update_subscriptions_mapping`), `:126` (unconditional replace), `:96`/`:110` (lookup + "No consumers")
- `backends/src/univention/provisioning/backends/nats_kv.py:100` (`get_keys`, swallows `NoKeysError`), `:107` (`get_all_subscriptions`)
- `nats/js/kv.py` `keys()` → `watchall`; `watch()` `num_pending == 0` caught-up logic
- `dispatcher/tests/test_dispatcher.py` (reproduction + guard tests)

Upstream:
- nats-server issue 4824 (wrong NumPending for last_per_subject consumers)
- nats.py issue 842 (kv.watch/history emits initial None too early → spurious NoKeysError; affected nats-py 2.14.0)
- nats.py PR 844 (`nats-key-value` package), releases through 2.15.0
- PyPI: `nats-key-value` 0.1.0, `nats-jetstream` 0.3.0
