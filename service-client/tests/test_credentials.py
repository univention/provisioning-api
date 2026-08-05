# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from __future__ import annotations

import json
import os
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from univention.provisioning.service_client import credentials
from univention.provisioning.service_client.credentials import (
    AdminCredentialError,
    binddn_to_username,
    read_local_admin_password,
    read_remote_admin_password,
)

ADMIN_PASSWORD = "admin-secret-value"
ADMIN_DN = "uid=Administrator,cn=users,dc=example,dc=test"


def _write_credentials(path, value=ADMIN_PASSWORD, *, mode=0o640):
    path.write_text(json.dumps({credentials.ADMIN_PASSWORD_KEY: value}))
    path.chmod(mode)


def _pretend_file_is_root_owned(monkeypatch):
    real_fstat = os.fstat

    def root_fstat(descriptor):
        metadata = real_fstat(descriptor)
        return SimpleNamespace(st_mode=metadata.st_mode, st_uid=0, st_size=metadata.st_size)

    monkeypatch.setattr(credentials.os, "fstat", root_fstat)


def test_read_local_admin_password_accepts_root_owned_group_readable_file(tmp_path, monkeypatch):
    path = tmp_path / "provisioning-secrets.json"
    _write_credentials(path)
    _pretend_file_is_root_owned(monkeypatch)

    assert read_local_admin_password(path) == ADMIN_PASSWORD


def test_read_local_admin_password_rejects_symlink(tmp_path):
    target = tmp_path / "target.json"
    link = tmp_path / "provisioning-secrets.json"
    _write_credentials(target)
    link.symlink_to(target)

    with pytest.raises(AdminCredentialError, match="safely open"):
        read_local_admin_password(link)


def test_read_local_admin_password_rejects_non_regular_file(tmp_path):
    with pytest.raises(AdminCredentialError, match="regular file"):
        read_local_admin_password(tmp_path)


def test_read_local_admin_password_rejects_non_root_owner(tmp_path):
    path = tmp_path / "provisioning-secrets.json"
    _write_credentials(path)

    with pytest.raises(AdminCredentialError, match="owned by root"):
        read_local_admin_password(path)


@pytest.mark.parametrize("mode", [0o644, 0o646, 0o660])
def test_read_local_admin_password_rejects_unsafe_permissions(tmp_path, monkeypatch, mode):
    path = tmp_path / "provisioning-secrets.json"
    _write_credentials(path, mode=mode)
    _pretend_file_is_root_owned(monkeypatch)

    with pytest.raises(AdminCredentialError, match="unsafe permissions"):
        read_local_admin_password(path)


def test_read_local_admin_password_rejects_oversized_file(tmp_path, monkeypatch):
    path = tmp_path / "provisioning-secrets.json"
    path.write_bytes(b"x" * (credentials.MAX_CREDENTIAL_FILE_BYTES + 1))
    path.chmod(0o600)
    _pretend_file_is_root_owned(monkeypatch)

    with pytest.raises(AdminCredentialError, match="unexpectedly large"):
        read_local_admin_password(path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"not json", "not valid JSON"),
        (b"[]", "JSON object"),
        (b"{}", "non-empty"),
        (json.dumps({credentials.ADMIN_PASSWORD_KEY: 42}).encode(), "non-empty"),
    ],
)
def test_read_local_admin_password_rejects_invalid_content(tmp_path, monkeypatch, content, message):
    path = tmp_path / "provisioning-secrets.json"
    path.write_bytes(content)
    path.chmod(0o600)
    _pretend_file_is_root_owned(monkeypatch)

    with pytest.raises(AdminCredentialError, match=message):
        read_local_admin_password(path)


@pytest.mark.parametrize("value", ["line1\nline2", "nul\x00byte", "x" * (credentials.MAX_ADMIN_PASSWORD_BYTES + 1)])
def test_read_local_admin_password_rejects_invalid_password_value(tmp_path, monkeypatch, value):
    path = tmp_path / "provisioning-secrets.json"
    _write_credentials(path, value)
    _pretend_file_is_root_owned(monkeypatch)

    with pytest.raises(AdminCredentialError, match=credentials.ADMIN_PASSWORD_KEY):
        read_local_admin_password(path)


@pytest.mark.parametrize(
    ("binddn", "username"),
    [
        (ADMIN_DN, "Administrator"),
        ("UID=admin-user,cn=users,dc=example,dc=test", "admin-user"),
        ("uid=user.name_1,cn=users,dc=example,dc=test", "user.name_1"),
    ],
)
def test_binddn_to_username_accepts_first_uid_rdn(binddn, username):
    assert binddn_to_username(binddn) == username


@pytest.mark.parametrize(
    "binddn",
    [
        "cn=admin,dc=example,dc=test",
        "cn=users,uid=Administrator,dc=example,dc=test",
        "uid=Administrator+cn=admin,dc=example,dc=test",
        "uid=-oProxyCommand,cn=users,dc=example,dc=test",
        "uid=user@example.test,cn=users,dc=example,dc=test",
        "not a dn",
        "",
    ],
)
def test_binddn_to_username_rejects_unsafe_or_non_user_dn(binddn):
    with pytest.raises(AdminCredentialError):
        binddn_to_username(binddn)


def test_binddn_to_username_has_safe_fallback_without_python_ldap(monkeypatch):
    monkeypatch.setattr(credentials, "_ldap_dn", None)

    assert binddn_to_username(ADMIN_DN) == "Administrator"


@pytest.mark.parametrize(
    "binddn",
    [
        "uid=Admin\\,istrator,cn=users,dc=example,dc=test",
        "uid=Administrator+cn=admin,dc=example,dc=test",
        "uid=Administrator",
    ],
)
def test_binddn_fallback_rejects_dn_forms_it_cannot_parse_safely(monkeypatch, binddn):
    monkeypatch.setattr(credentials, "_ldap_dn", None)

    with pytest.raises(AdminCredentialError):
        binddn_to_username(binddn)


def test_read_remote_admin_password_uses_strict_host_key_checking_and_fixed_list_argv():
    runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=(ADMIN_PASSWORD + "\n").encode()))

    assert read_remote_admin_password("primary.example.test", ADMIN_DN, "/tmp/bind-password", runner) == ADMIN_PASSWORD

    runner.assert_called_once_with(
        [
            credentials.UNIVENTION_SSH,
            "--strict-host-key-checking",
            "--no-split",
            "-timeout",
            "60",
            "/tmp/bind-password",
            "Administrator@primary.example.test",
            credentials.REMOTE_ADMIN_COMMAND,
        ],
        check=False,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=70,
    )
    assert "env" not in runner.call_args.kwargs


def test_read_remote_admin_password_accepts_one_line_without_terminal_newline():
    runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=ADMIN_PASSWORD.encode()))

    assert read_remote_admin_password("primary.example.test", ADMIN_DN, "/tmp/bind-password", runner) == ADMIN_PASSWORD


@pytest.mark.parametrize(
    "stdout",
    [
        b"",
        b"\n",
        b"   \n",
        b"first\nsecond\n",
        b"first\r\n",
        b"nul\x00byte\n",
        b"x" * (credentials.MAX_ADMIN_PASSWORD_BYTES + 2),
        b"\xff\n",
        None,
    ],
)
def test_read_remote_admin_password_rejects_invalid_or_unbounded_stdout(stdout):
    runner = Mock(return_value=SimpleNamespace(returncode=0, stdout=stdout))

    with pytest.raises(AdminCredentialError):
        read_remote_admin_password("primary.example.test", ADMIN_DN, "/tmp/bind-password", runner)


def test_read_remote_admin_password_does_not_expose_failed_stdout():
    leaked = "must-not-be-in-the-error"
    runner = Mock(return_value=SimpleNamespace(returncode=255, stdout=leaked.encode()))

    with pytest.raises(AdminCredentialError) as exc_info:
        read_remote_admin_password("primary.example.test", ADMIN_DN, "/tmp/bind-password", runner)

    assert leaked not in str(exc_info.value)


@pytest.mark.parametrize("exception", [OSError("ssh unavailable"), subprocess.TimeoutExpired(["ssh"], 70)])
def test_read_remote_admin_password_maps_runner_failures(exception):
    runner = Mock(side_effect=exception)

    with pytest.raises(AdminCredentialError, match="Could not obtain"):
        read_remote_admin_password("primary.example.test", ADMIN_DN, "/tmp/bind-password", runner)


@pytest.mark.parametrize(
    "server",
    [
        "primary",
        "-primary.example.test",
        "primary..example.test",
        "primary.example.test.",
        "primary.example.test;id",
        "127.0.0.1",
        "prímary.example.test",
        "",
    ],
)
def test_read_remote_admin_password_rejects_invalid_server_before_running(server):
    runner = Mock()

    with pytest.raises(AdminCredentialError):
        read_remote_admin_password(server, ADMIN_DN, "/tmp/bind-password", runner)

    runner.assert_not_called()


@pytest.mark.parametrize("bindpwdfile", ["relative-password", "/tmp/bad\npath"])
def test_read_remote_admin_password_rejects_invalid_password_file_path(bindpwdfile):
    runner = Mock()

    with pytest.raises(AdminCredentialError):
        read_remote_admin_password("primary.example.test", ADMIN_DN, bindpwdfile, runner)

    runner.assert_not_called()


def test_read_remote_admin_password_rejects_invalid_binddn_before_running():
    runner = Mock()

    with pytest.raises(AdminCredentialError):
        read_remote_admin_password(
            "primary.example.test",
            "cn=admin,dc=example,dc=test",
            "/tmp/bind-password",
            runner,
        )

    runner.assert_not_called()
