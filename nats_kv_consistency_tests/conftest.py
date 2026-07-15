# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Fixtures for the standalone NATS KV consistency reproduction suite.

These tests talk to a *real* 3-node JetStream cluster with the ``nats-py``
client directly. They deliberately do **not** import any provisioning code, so
the reproduction is isolated to the NATS client / server behaviour.

The whole point of the reproduction is that the KV enumeration is read from a
*different* cluster node than the one the keys were written to. The two
endpoints are configured independently:

======================  =====================================  ==============================
env var                 default (inside the compose network)   host-side (published ports)
======================  =====================================  ==============================
``KV_WRITE_URL``        ``nats://nats1:4222``                  ``nats://localhost:4222`` (nats1)
``KV_READ_URL``         ``nats://nats3:4222``                  ``nats://localhost:4223`` (nats3)
``KV_USER``             ``admin``                              ``admin``
``KV_PASSWORD``         ``univention``                         ``univention``
``KV_REPLICAS``         ``3``                                  ``3``
``KV_ROUNDS``           ``40``                                 ``40``
``KV_KEYS_PER_ROUND``   ``25``                                 ``25``
======================  =====================================  ==============================

Run from inside the compose network (e.g. a container attached to the same
network as ``nats1``/``nats2``/``nats3``)::

    pytest nats_kv_consistency_tests -v

Run from the host against the published ports::

    KV_WRITE_URL=nats://localhost:4222 KV_READ_URL=nats://localhost:4223 \
        pytest nats_kv_consistency_tests -v

If neither endpoint can be reached the whole suite is skipped (never failed),
so it is safe to collect anywhere.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from dataclasses import dataclass
from typing import AsyncGenerator

import nats
import pytest
import pytest_asyncio
from nats.aio.client import Client as NatsClient
from nats.js import JetStreamContext
from nats.js.api import KeyValueConfig
from nats.js.errors import NotFoundError


@dataclass(frozen=True)
class ClusterConfig:
    write_url: str
    read_url: str
    user: str
    password: str
    replicas: int
    rounds: int
    keys_per_round: int


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return int(raw)


@pytest.fixture(scope="session")
def cluster() -> ClusterConfig:
    return ClusterConfig(
        write_url=os.environ.get("KV_WRITE_URL", "nats://nats1:4222"),
        read_url=os.environ.get("KV_READ_URL", "nats://nats3:4222"),
        user=os.environ.get("KV_USER", "admin"),
        password=os.environ.get("KV_PASSWORD", "univention"),
        replicas=_env_int("KV_REPLICAS", 3),
        rounds=_env_int("KV_ROUNDS", 40),
        keys_per_round=_env_int("KV_KEYS_PER_ROUND", 25),
    )


async def _connect(url: str, cfg: ClusterConfig) -> NatsClient:
    """Connect to a single, explicit node, pinned there (no failover).

    ``connect(..., servers=[url])`` plus ``dont_randomize`` keeps the client on
    exactly the node we asked for, which is essential: the reproduction depends
    on the write connection and the read connection landing on *different*
    cluster nodes.
    """
    try:
        # Hard outer bound: nats-py's connect_timeout does not cover a hanging
        # DNS lookup, so wrap the whole connect to guarantee a fast skip when the
        # cluster is not reachable (e.g. collected outside the compose network).
        return await asyncio.wait_for(
            nats.connect(
                servers=[url],
                user=cfg.user,
                password=cfg.password,
                allow_reconnect=False,
                dont_randomize=True,
                connect_timeout=5,
            ),
            timeout=10,
        )
    except Exception as exc:  # noqa: BLE001 - surfaced as a skip, not a failure
        pytest.skip(f"NATS node {url!r} not reachable ({exc!r}); skipping cluster repro suite")


@pytest_asyncio.fixture
async def write_nc(cluster: ClusterConfig) -> AsyncGenerator[NatsClient, None]:
    nc = await _connect(cluster.write_url, cluster)
    try:
        yield nc
    finally:
        await nc.close()


@pytest_asyncio.fixture
async def read_nc(cluster: ClusterConfig) -> AsyncGenerator[NatsClient, None]:
    nc = await _connect(cluster.read_url, cluster)
    try:
        yield nc
    finally:
        await nc.close()


@pytest_asyncio.fixture
async def write_js(write_nc: NatsClient) -> JetStreamContext:
    return write_nc.jetstream()


@pytest_asyncio.fixture
async def read_js(read_nc: NatsClient) -> JetStreamContext:
    return read_nc.jetstream()


@pytest_asyncio.fixture
async def kv_bucket(
    cluster: ClusterConfig,
    write_js: JetStreamContext,
    read_js: JetStreamContext,
) -> AsyncGenerator[str, None]:
    """Create a fresh, uniquely named KV bucket on the *write* node and make
    sure it is visible on the *read* node before the test starts.

    Mirrors the provisioning ``SUBSCRIPTIONS`` bucket shape (``history=1``) but
    with a configurable replica count so the cross-node read path is exercised.
    """
    bucket = f"REPRO_{uuid.uuid4().hex[:12]}"
    await write_js.create_key_value(config=KeyValueConfig(bucket=bucket, history=1, replicas=cluster.replicas))

    # The bucket is a replicated stream; wait until the read node can see it so
    # a genuinely-missing bucket is never confused with the enumeration bug.
    await _await_bucket_visible(read_js, bucket)

    try:
        yield bucket
    finally:
        try:
            await write_js.delete_key_value(bucket)
        except NotFoundError:
            pass


async def _await_bucket_visible(js: JetStreamContext, bucket: str, attempts: int = 50) -> None:
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            await js.key_value(bucket)
            return
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            await _sleep(0.1)
    raise AssertionError(f"KV bucket {bucket!r} never became visible on the read node: {last_exc!r}")


async def _sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)
