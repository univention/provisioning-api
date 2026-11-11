# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import base64
import ssl
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

from univention.provisioning.consumer.kubernetes_secrets import (
    InvalidReference,
    KubernetesSecretReader,
    SecretReadError,
    SecretReference,
    is_reference,
    parse_reference,
)

NAMESPACE = "nubus"
SECRETS_PATH = f"/api/v1/namespaces/{NAMESPACE}/secrets"


def b64(value: bytes | str) -> str:
    return base64.b64encode(value.encode() if isinstance(value, str) else value).decode()


@pytest.fixture
async def reader(httpserver: HTTPServer):
    reader = KubernetesSecretReader(httpserver.url_for("/"), NAMESPACE, "sa-token", ssl_context=None)
    yield reader
    await reader.close()


class TestParseReference:
    def test_valid(self):
        reference = parse_reference({"kubernetesSecret": {"name": "portal-consumer", "key": "password"}})
        assert reference == SecretReference(name="portal-consumer", key="password")

    @pytest.mark.parametrize(
        "value",
        [
            {"kubernetesSecret": {"name": "s"}},
            {"kubernetesSecret": {"key": "k"}},
            {"kubernetesSecret": {"name": "s", "key": "k", "namespace": "other"}},
            {"kubernetesSecret": {"name": "", "key": "k"}},
            {"kubernetesSecret": {"name": "s", "key": 1}},
            {"kubernetesSecret": "s"},
            {"kubernetesSecret": {"name": "s", "key": "k"}, "default": "x"},
        ],
    )
    def test_invalid(self, value):
        assert is_reference(value)
        with pytest.raises(InvalidReference):
            parse_reference(value)

    @pytest.mark.parametrize("value", ["password", None, {"name": "s", "key": "k"}, ["kubernetesSecret"]])
    def test_not_a_reference(self, value):
        assert not is_reference(value)


class TestKubernetesSecretReader:
    async def test_decodes_the_key_and_sends_the_token(self, httpserver: HTTPServer, reader):
        httpserver.expect_request(
            f"{SECRETS_PATH}/portal-consumer", headers={"Authorization": "Bearer sa-token"}
        ).respond_with_json({"data": {"password": b64("pä$$: wörd")}})

        assert await reader.get(SecretReference("portal-consumer", "password")) == "pä$$: wörd"

    async def test_reads_each_secret_once(self, httpserver: HTTPServer, reader):
        httpserver.expect_ordered_request(f"{SECRETS_PATH}/shared").respond_with_json(
            {"data": {"a": b64("one"), "b": b64("two")}}
        )

        assert await reader.get(SecretReference("shared", "a")) == "one"
        assert await reader.get(SecretReference("shared", "b")) == "two"
        assert len(httpserver.log) == 1

    async def test_missing_key(self, httpserver: HTTPServer, reader):
        httpserver.expect_request(f"{SECRETS_PATH}/s").respond_with_json({"data": {"other": b64("x")}})

        with pytest.raises(SecretReadError, match="Secret 's' has no key 'password'") as error:
            await reader.get(SecretReference("s", "password"))
        assert not error.value.transient

    async def test_secret_without_data(self, httpserver: HTTPServer, reader):
        httpserver.expect_request(f"{SECRETS_PATH}/s").respond_with_json({"metadata": {"name": "s"}})

        with pytest.raises(SecretReadError, match="no key"):
            await reader.get(SecretReference("s", "password"))

    async def test_not_utf8(self, httpserver: HTTPServer, reader):
        httpserver.expect_request(f"{SECRETS_PATH}/s").respond_with_json({"data": {"password": b64(b"\xff\xfe")}})

        with pytest.raises(SecretReadError, match="not UTF-8"):
            await reader.get(SecretReference("s", "password"))

    @pytest.mark.parametrize(
        "status,message,transient",
        [
            (404, "Secret 's' in namespace 'nubus' not found", False),
            (403, "Access to Secret 's' in namespace 'nubus' denied", False),
            (401, "denied", False),
            (500, "failed with HTTP 500", True),
            (503, "failed with HTTP 503", True),
            (400, "failed with HTTP 400", False),
        ],
    )
    async def test_api_errors(self, httpserver: HTTPServer, reader, status, message, transient):
        httpserver.expect_request(f"{SECRETS_PATH}/s").respond_with_data("nope", status=status)

        with pytest.raises(SecretReadError, match=message) as error:
            await reader.get(SecretReference("s", "password"))
        assert error.value.transient is transient


class TestFromServiceAccount:
    def test_reads_namespace_token_and_service_address(self, tmp_path: Path, monkeypatch):
        ca = ssl.get_default_verify_paths().openssl_cafile
        if not Path(ca).is_file():
            pytest.skip("no system CA bundle to stand in for ca.crt")
        (tmp_path / "namespace").write_text("nubus\n")
        (tmp_path / "token").write_text("sa-token\n")
        (tmp_path / "ca.crt").write_bytes(Path(ca).read_bytes())

        async def build():
            reader = KubernetesSecretReader.from_service_account(
                tmp_path, {"KUBERNETES_SERVICE_HOST": "fd00::1", "KUBERNETES_SERVICE_PORT": "443"}
            )
            await reader.close()
            return reader

        import asyncio

        reader = asyncio.run(build())
        assert reader.namespace == "nubus"
        assert reader.api_url == "https://[fd00::1]:443"

    def test_without_service_account(self, tmp_path: Path):
        with pytest.raises(SecretReadError, match="ServiceAccount token"):
            KubernetesSecretReader.from_service_account(tmp_path, {})
