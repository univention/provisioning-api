# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
`kubernetes_secret` references and a reader for the Secrets they name.

A reference replaces a value: `{"kubernetes_secret": {"name": "<Secret>", "key": "<key>"}}`.
The rules match the data-loader's in stack-data.
"""

import base64
import os
import ssl
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import aiohttp

REFERENCE_KEY = "kubernetes_secret"
REFERENCE_FIELDS = {"name", "key"}
SERVICE_ACCOUNT_DIR = Path("/var/run/secrets/kubernetes.io/serviceaccount")


class InvalidReference(ValueError):
    pass


class SecretReadError(RuntimeError):
    """A referenced Secret or key could not be read. The message never contains the value."""

    def __init__(self, message: str, transient: bool = False):
        super().__init__(message)
        self.transient = transient


@dataclass(frozen=True)
class SecretReference:
    name: str
    key: str

    def __str__(self) -> str:
        return f"Secret {self.name!r} key {self.key!r}"


def is_reference(value: Any) -> bool:
    return isinstance(value, dict) and REFERENCE_KEY in value


def parse_reference(value: Any) -> SecretReference:
    spec = value.get(REFERENCE_KEY) if isinstance(value, dict) else None
    if (
        not isinstance(value, dict)
        or len(value) != 1
        or not isinstance(spec, dict)
        or set(spec) != REFERENCE_FIELDS
        or not all(isinstance(spec[field], str) and spec[field] for field in REFERENCE_FIELDS)
    ):
        raise InvalidReference(
            f"expected {{{REFERENCE_KEY!r}: {{'name': <non-empty string>, 'key': <non-empty string>}}}}"
        )
    return SecretReference(name=spec["name"], key=spec["key"])


class KubernetesSecretReader:
    """Reads Secrets from one namespace through the Kubernetes API, once per Secret."""

    def __init__(self, api_url: str, namespace: str, token: str, ssl_context: ssl.SSLContext | None, timeout=10):
        self.api_url = api_url.rstrip("/")
        self.namespace = namespace
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {token}"},
            connector=aiohttp.TCPConnector(ssl=ssl_context if ssl_context is not None else True),
            timeout=aiohttp.ClientTimeout(total=timeout),
        )
        self._secrets: dict[str, dict[str, str]] = {}

    @classmethod
    def from_service_account(
        cls,
        directory: Path = SERVICE_ACCOUNT_DIR,
        environ: Mapping[str, str] = os.environ,
    ) -> "KubernetesSecretReader":
        try:
            namespace = (directory / "namespace").read_text().strip()
            token = (directory / "token").read_text().strip()
            host = environ["KUBERNETES_SERVICE_HOST"]
            port = environ["KUBERNETES_SERVICE_PORT"]
        except (OSError, KeyError) as error:
            raise SecretReadError(
                f"No in-cluster Kubernetes credentials ({error}). "
                "Reading a referenced Secret needs the pod's ServiceAccount token.",
            ) from None
        if ":" in host:
            host = f"[{host}]"
        ssl_context = ssl.create_default_context(cafile=str(directory / "ca.crt"))
        return cls(f"https://{host}:{port}", namespace, token, ssl_context)

    async def close(self):
        await self.session.close()

    async def get(self, reference: SecretReference) -> str:
        if reference.name not in self._secrets:
            self._secrets[reference.name] = await self._fetch(reference.name)
        data = self._secrets[reference.name]
        if reference.key not in data:
            raise SecretReadError(f"Secret {reference.name!r} has no key {reference.key!r}")
        try:
            return base64.b64decode(data[reference.key]).decode("utf-8")
        except UnicodeDecodeError:
            raise SecretReadError(f"Secret {reference.name!r} key {reference.key!r} is not UTF-8") from None

    async def _fetch(self, name: str) -> dict[str, str]:
        where = f"Secret {name!r} in namespace {self.namespace!r}"
        url = f"{self.api_url}/api/v1/namespaces/{self.namespace}/secrets/{name}"
        async with self.session.get(url) as response:
            if response.status == 200:
                return (await response.json()).get("data") or {}
            if response.status == 404:
                raise SecretReadError(f"{where} not found")
            if response.status in (401, 403):
                raise SecretReadError(f"Access to {where} denied (HTTP {response.status})")
            raise SecretReadError(
                f"Reading {where} failed with HTTP {response.status}",
                transient=response.status >= 500,
            )
