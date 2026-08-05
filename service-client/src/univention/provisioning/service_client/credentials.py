# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Securely obtain Provisioning Service administrative credentials."""

from __future__ import annotations

import ipaddress
import json
import os
import re
import stat
import subprocess
from collections.abc import Callable
from typing import Any

try:
    import ldap.dn as _ldap_dn
except ImportError:  # pragma: no cover - python-ldap is available on UCS
    _ldap_dn = None


ADMIN_PASSWORD_KEY = "PROVISIONING_API_ADMIN_PASSWORD"
DEFAULT_ADMIN_CREDENTIAL_FILE = "/etc/provisioning-secrets.json"
MAX_CREDENTIAL_FILE_BYTES = 64 * 1024
MAX_ADMIN_PASSWORD_BYTES = 4096
REMOTE_ADMIN_COMMAND = "/usr/sbin/univention-provisioning-service-client _read-admin-password"
UNIVENTION_SSH = "/usr/sbin/univention-ssh"

_USERNAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}\Z")
_DNS_LABEL_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z")


class AdminCredentialError(RuntimeError):
    """The Provisioning administrative credential could not be obtained safely."""


def _read_bounded_file(descriptor: int, maximum: int) -> bytes:
    content = bytearray()
    while len(content) <= maximum:
        chunk = os.read(descriptor, min(8192, maximum + 1 - len(content)))
        if not chunk:
            return bytes(content)
        content.extend(chunk)
    raise AdminCredentialError("Provisioning admin credential file is unexpectedly large")


def _validate_password(value: Any, *, source: str) -> str:
    if not isinstance(value, str) or not value:
        raise AdminCredentialError(f"{source} does not contain a non-empty {ADMIN_PASSWORD_KEY}")
    try:
        encoded = value.encode("utf-8")
    except UnicodeEncodeError:
        raise AdminCredentialError(f"{source} contains an invalid {ADMIN_PASSWORD_KEY}") from None
    if len(encoded) > MAX_ADMIN_PASSWORD_BYTES:
        raise AdminCredentialError(f"{source} contains an unexpectedly large {ADMIN_PASSWORD_KEY}")
    if "\x00" in value or "\r" in value or "\n" in value:
        raise AdminCredentialError(f"{source} contains an invalid {ADMIN_PASSWORD_KEY}")
    return value


def read_local_admin_password(path: str | os.PathLike[str] = DEFAULT_ADMIN_CREDENTIAL_FILE) -> str:
    """Read the admin password from a trusted, bounded local JSON file."""

    credential_path = os.fspath(path)
    try:
        no_follow = os.O_NOFOLLOW
    except AttributeError as exc:  # pragma: no cover - UCS is Linux
        raise AdminCredentialError("The platform cannot safely open the Provisioning admin credential file") from exc

    try:
        descriptor = os.open(credential_path, os.O_RDONLY | os.O_CLOEXEC | no_follow)
    except OSError as exc:
        raise AdminCredentialError("Cannot safely open the Provisioning admin credential file") from exc

    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise AdminCredentialError("Provisioning admin credential path is not a regular file")
        if metadata.st_uid != 0:
            raise AdminCredentialError("Provisioning admin credential file is not owned by root")
        if metadata.st_mode & (stat.S_IROTH | stat.S_IWGRP | stat.S_IWOTH):
            raise AdminCredentialError("Provisioning admin credential file has unsafe permissions")
        if metadata.st_size > MAX_CREDENTIAL_FILE_BYTES:
            raise AdminCredentialError("Provisioning admin credential file is unexpectedly large")
        raw = _read_bounded_file(descriptor, MAX_CREDENTIAL_FILE_BYTES)
    finally:
        os.close(descriptor)

    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise AdminCredentialError("Provisioning admin credential file is not valid JSON") from None
    if not isinstance(data, dict):
        raise AdminCredentialError("Provisioning admin credential file does not contain a JSON object")
    return _validate_password(data.get(ADMIN_PASSWORD_KEY), source="Provisioning admin credential file")


def _fallback_first_rdn(binddn: str) -> tuple[str, str]:
    """Parse the safe subset needed for UCS user DNs when python-ldap is absent."""

    first_rdn, separator, remainder = binddn.partition(",")
    if not separator or not remainder or "\\" in first_rdn or "+" in first_rdn:
        raise AdminCredentialError("The bind DN is not a supported UCS user DN")
    attribute, equals, value = first_rdn.partition("=")
    if not equals or "=" in value:
        raise AdminCredentialError("The bind DN is not a supported UCS user DN")
    return attribute.strip(), value


def binddn_to_username(binddn: str) -> str:
    """Return the username only when the bind DN starts with one ``uid`` RDN."""

    if not isinstance(binddn, str) or not binddn or "\x00" in binddn:
        raise AdminCredentialError("A valid bind DN is required for remote Provisioning administration")

    if _ldap_dn is None:
        attribute, username = _fallback_first_rdn(binddn)
    else:
        try:
            parsed = _ldap_dn.str2dn(binddn)
        except Exception as exc:
            raise AdminCredentialError("The bind DN is not a valid LDAP DN") from exc
        if not parsed or len(parsed[0]) != 1:
            raise AdminCredentialError("The bind DN must start with one uid RDN")
        attribute, username, _flags = parsed[0][0]

    if attribute.casefold() != "uid":
        raise AdminCredentialError("The bind DN must start with a uid RDN")
    if not isinstance(username, str) or not _USERNAME_RE.fullmatch(username):
        raise AdminCredentialError("The bind DN contains an unsupported remote username")
    return username


def _validate_server(server: str) -> str:
    if not isinstance(server, str) or not server or len(server) > 253 or server.endswith("."):
        raise AdminCredentialError("A valid Provisioning server FQDN is required")
    if server.casefold() != server.lower():
        # ``lower`` and ``casefold`` differ for non-ASCII input; DNS names here
        # must use their ASCII/IDNA representation.
        raise AdminCredentialError("A valid Provisioning server FQDN is required")
    try:
        server.encode("ascii")
    except UnicodeEncodeError as exc:
        raise AdminCredentialError("A valid Provisioning server FQDN is required") from exc
    try:
        ipaddress.ip_address(server)
    except ValueError:
        pass
    else:
        raise AdminCredentialError("The Provisioning server must be an FQDN, not an IP address")
    labels = server.split(".")
    if len(labels) < 2 or any(not _DNS_LABEL_RE.fullmatch(label) for label in labels):
        raise AdminCredentialError("A valid Provisioning server FQDN is required")
    return server


def _validate_bindpwdfile(bindpwdfile: str | os.PathLike[str]) -> str:
    password_file = os.fspath(bindpwdfile)
    if not isinstance(password_file, str) or not os.path.isabs(password_file):
        raise AdminCredentialError("The bind password file path must be absolute")
    if "\x00" in password_file or "\r" in password_file or "\n" in password_file:
        raise AdminCredentialError("The bind password file path is invalid")
    return password_file


def read_remote_admin_password(
    server: str,
    binddn: str,
    bindpwdfile: str | os.PathLike[str],
    runner: Callable[..., Any] = subprocess.run,
) -> str:
    """Read the admin password over SSH without persisting it on this host."""

    validated_server = _validate_server(server)
    username = binddn_to_username(binddn)
    password_file = _validate_bindpwdfile(bindpwdfile)
    argv = [
        UNIVENTION_SSH,
        "--strict-host-key-checking",
        "--no-split",
        "-timeout",
        "60",
        password_file,
        f"{username}@{validated_server}",
        REMOTE_ADMIN_COMMAND,
    ]

    try:
        result = runner(
            argv,
            check=False,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=70,
        )
    except (OSError, subprocess.SubprocessError):
        raise AdminCredentialError(
            "Could not obtain the Provisioning admin credential from the remote server"
        ) from None

    if result.returncode != 0:
        raise AdminCredentialError("Remote Provisioning admin credential lookup failed")

    stdout = result.stdout
    if isinstance(stdout, str):
        try:
            raw = stdout.encode("utf-8")
        except UnicodeEncodeError:
            raise AdminCredentialError("Remote Provisioning admin credential response is invalid") from None
    elif isinstance(stdout, bytes):
        raw = stdout
    else:
        raise AdminCredentialError("Remote Provisioning admin credential response is missing")

    if len(raw) > MAX_ADMIN_PASSWORD_BYTES + 1:
        raise AdminCredentialError("Remote Provisioning admin credential response is unexpectedly large")
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    if not raw or b"\n" in raw or b"\r" in raw or b"\x00" in raw:
        raise AdminCredentialError("Remote Provisioning admin credential response is not one non-empty line")
    try:
        password = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise AdminCredentialError("Remote Provisioning admin credential response is not valid UTF-8") from None
    if password != password.strip():
        raise AdminCredentialError("Remote Provisioning admin credential response has surrounding whitespace")
    return _validate_password(password, source="Remote Provisioning admin credential response")
