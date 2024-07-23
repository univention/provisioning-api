# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import uuid
from typing import Any, AsyncGenerator, Callable, Coroutine, NamedTuple

import msgpack
import nats
import pytest
from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError
from univention.admin.rest.client import UDM, HTTPError, NotFound
from univention.provisioning.consumer import AsyncClient, Settings

from ..conftest import REALMS_TOPICS


class E2ETestSettings(NamedTuple):
    provisioning_api_base_url: str
    provisioning_admin_username: str
    provisioning_admin_password: str

    provisioning_events_username: str
    provisioning_events_password: str

    nats_url: str
    nats_user: str
    nats_password: str

    ldap_server_uri: str
    ldap_base: str
    ldap_bind_dn: str
    ldap_bind_password: str

    udm_rest_api_base_url: str
    udm_rest_api_username: str
    udm_rest_api_password: str


def pytest_addoption(parser):
    # Portal tests options
    parser.addoption(
        "--environment",
        default="local",
        help=(
            "set the environment you are running the tests in."
            "accepted values are: 'local', 'dev-env', 'pipeline' and 'gaia'"
        ),
    )


@pytest.fixture(scope="session")
def test_settings(pytestconfig) -> E2ETestSettings:
    environment = pytestconfig.option.environment
    assert environment in (
        "local",
        "dev-env",
        "pipeline",
        "gaia",
        "gaia_nubus",
    ), "invalid value for --environment"

    with open("./tests/e2e/e2e_settings.json") as f:
        json_settings = json.load(f)

    settings = E2ETestSettings(**json_settings["local"])
    if environment == "local":
        return settings

    return settings._replace(**json_settings[environment])


@pytest.fixture(scope="session")
def udm(test_settings: E2ETestSettings) -> UDM:
    udm = UDM(
        test_settings.udm_rest_api_base_url,
        test_settings.udm_rest_api_username,
        test_settings.udm_rest_api_password,
    )
    # test the connection
    udm.get_ldap_base()
    return udm


@pytest.fixture(scope="session")
def ldap_base(udm) -> str:
    return udm.get_ldap_base()


@pytest.fixture
def subscriber_name() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def subscriber_password() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def client_settings(test_settings: E2ETestSettings, subscriber_name, subscriber_password) -> Settings:
    return Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=subscriber_name,
        provisioning_api_password=subscriber_password,
    )


@pytest.fixture
def admin_client_settings(test_settings: E2ETestSettings) -> Settings:
    return Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=test_settings.provisioning_admin_username,
        provisioning_api_password=test_settings.provisioning_admin_password,
    )


@pytest.fixture
async def provisioning_client(
    client_settings,
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(client_settings) as client:
        yield client


@pytest.fixture
async def provisioning_admin_client(
    admin_client_settings,
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(admin_client_settings) as client:
        yield client


@pytest.fixture
async def simple_subscription(
    subscriber_name,
    subscriber_password,
    provisioning_admin_client: AsyncClient,
) -> AsyncGenerator[str, Any]:
    await provisioning_admin_client.create_subscription(
        name=subscriber_name,
        password=subscriber_password,
        realms_topics=REALMS_TOPICS,
        request_prefill=False,
    )

    yield subscriber_name

    await provisioning_admin_client.cancel_subscription(subscriber_name)


@pytest.fixture(scope="session")
def maildomain(udm):
    name = "ldif-producer.unittests"
    domains = udm.get("mail/domain")
    if maildomains := list(domains.search(f"name={name}")):
        maildomain = domains.get(maildomains[0].dn)
        print(f"Using existing mail domain {maildomain!r}.")
    else:
        maildomain = domains.new()
        maildomain.properties.update({"name": name})
        maildomain.save()
        print(f"Created new mail domain {maildomain!r}.")
    yield name
    maildomain.delete()
    print(f"Deleted mail domain {maildomain!r}.")


@pytest.fixture()
async def nats_connection(test_settings: E2ETestSettings) -> AsyncGenerator[NATS, Any]:
    nc = NATS()
    await nc.connect(
        servers=test_settings.nats_url,
        user=test_settings.nats_user,
        password=test_settings.nats_password,
        max_reconnect_attempts=1,
        connect_timeout=5,
    )
    yield nc
    await nc.close()


@pytest.fixture(scope="session")
def ldif_producer_stream_name() -> str:
    return "stream:ldif-producer"


@pytest.fixture
def get_and_delete_all_messages(
    nats_connection,
) -> Callable[[str], AsyncGenerator[dict[str, Any], Any]]:
    """Retrieve all messages of a streamm (iterator) and delete them."""

    async def _get_and_delete_all_messages(
        stream_name: str,
    ) -> AsyncGenerator[dict[str, Any], Any]:
        manager = nats.js.manager.JetStreamManager(nats_connection)
        info = await manager.stream_info(stream_name)
        for seq_id in range(info.state.first_seq, info.state.last_seq + 1):
            try:
                raw_msg = await manager.get_msg(stream_name, seq_id)
            except NotFoundError:
                print(seq_id, "NOT FOUND")
                continue
            msg = msgpack.unpackb(raw_msg.data)
            _print(msg["body"])
            yield msg["body"]
            await manager.delete_msg(stream_name, seq_id)

    def _print(body):
        old = body["old"]
        new = body["new"]
        old_dn = old["entryDN"][0].decode() if old else ""
        new_dn = new["entryDN"][0].decode() if new else ""
        msg_id = body["message_id"]
        req_id = body["request_id"]
        req_type = body["ldap_request_type"]
        print(f"msg: [{msg_id}][{req_id}] {req_type:<6} | old DN: {old_dn!r} | new DN: {new_dn!r}")
        if req_type in ("MODIFY", "MODRDN"):
            if not old:
                print("                        | !!! old=None")
                return
            diff: dict[str, tuple[Any, Any]] = {}
            for k, v in old.items():
                if k in {"entryCSN", "modifyTimestamp"}:
                    continue
                if k not in new:
                    diff[k] = (v, None)
                    continue
                if v != new[k]:
                    diff[k] = (v, new[k])
            for k, v in new.items():
                if k not in old:
                    diff[k] = (None, v)
            print(f"                        | diff: {diff!r}")

    return _get_and_delete_all_messages


@pytest.fixture
def purge_stream(nats_connection):
    """Delete all messages from stream."""

    async def _purge_stream(stream_name: str):
        manager = nats.js.manager.JetStreamManager(nats_connection)
        await manager.purge_stream(stream_name)
        print(f"Purged NATS stream {stream_name!r}.")

    return _purge_stream


@pytest.fixture(autouse=True)
async def auto_purge_stream(ldif_producer_stream_name, purge_stream):
    await purge_stream(ldif_producer_stream_name)


@pytest.fixture
def delete_udm_object(udm: UDM) -> Callable[[str, str], Coroutine[Any, Any, None]]:
    async def _delete_udm_object(udm_module: str, dn: str):
        mod = udm.get(udm_module)
        try:
            obj = mod.get(dn)
            obj.delete()
        except NotFound:
            print(f"Object doesn't exist: {udm_module!r}: {dn!r}.")
        except HTTPError as exc:
            print(f"HTTPError: {exc.response!r} | {exc.error_details!r} | {exc!s}")
        else:
            print(f"Deleted {udm_module!r}: {dn!r}.")

    return _delete_udm_object


@pytest.fixture
async def schedule_delete_udm_object(delete_udm_object) -> Callable[[str, str], None]:
    objects: list[tuple[str, str]] = []

    def _schedule_delete_udm_object(udm_module: str, dn: str):
        objects.append((udm_module, dn))

    yield _schedule_delete_udm_object

    for udm_module_, dn_ in objects:
        await delete_udm_object(udm_module_, dn_)


@pytest.fixture(scope="session")
def udm_module_exists(udm: UDM) -> Callable[[str], bool]:
    def _udm_module_exists(module_name: str) -> bool:
        return module_name in {m.name for m in udm.modules()}

    return _udm_module_exists
