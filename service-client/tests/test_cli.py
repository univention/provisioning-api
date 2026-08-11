# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from __future__ import annotations

import json
from argparse import Namespace
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from univention.provisioning.service_client import cli
from univention.provisioning.service_client.credentials import AdminCredentialError
from univention.provisioning.service_client.manager import SubscriptionOutcome
from univention.provisioning.service_client.models import SubscriptionDefinition
from univention.provisioning.service_client.storage import SubscriptionRecord, SubscriptionStore

SERVER = "primary.example.test"
BACKUP_SERVER = "backup.example.test"
DEFINITION = json.dumps(
    {
        "name": "ox-connector-member",
        "realms_topics": [{"realm": "udm", "topic": "users/user"}],
        "request_prefill": False,
        "password": "ignored-input-secret",
        "password_file": "/tmp/ignored",
    }
)


def subscribe_args(tmp_path, *extra: str) -> list[str]:
    return [
        "subscribe",
        "--json",
        DEFINITION,
        "--subscription-file",
        str(tmp_path / "runtime-secrets" / "subscription.json"),
        "--provisioning-server",
        SERVER,
        "--generate-password",
        *extra,
    ]


def saved_subscription(tmp_path, *, server: str = BACKUP_SERVER):
    path = tmp_path / "runtime-secrets" / "subscription.json"
    definition = SubscriptionDefinition.from_json(DEFINITION)
    record = SubscriptionRecord.candidate(
        base_url=f"https://{server}/univention/provisioning",
        definition=definition,
        password="limited-subscriber-secret",
    ).activate()
    store = SubscriptionStore(path)
    store.save(record)
    return path, store, record


def test_parser_accepts_all_appcenter_prescript_arguments(tmp_path):
    args = cli.build_parser().parse_args(
        subscribe_args(
            tmp_path,
            "--binddn",
            "uid=Administrator,cn=users,dc=example,dc=test",
            "--bindpwdfile",
            "/tmp/password",
            "--error-file",
            "/tmp/error",
            "--locale",
            "de_DE.UTF-8",
            "--old-version",
            "3.0",
            "--version",
            "4.0",
        )
    )

    assert args.binddn.startswith("uid=Administrator")
    assert args.old_version == "3.0"
    assert args.version == "4.0"


def test_parser_rejects_misspelled_client_option(tmp_path):
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(subscribe_args(tmp_path, "--generate-passwor"))


def test_remote_admin_provider_is_lazy_and_forwards_only_authentication_inputs(monkeypatch):
    lookup = Mock(return_value="admin-secret")
    monkeypatch.setattr(cli, "_is_local_server", lambda server: False)
    monkeypatch.setattr(cli, "read_remote_admin_password", lookup)
    args = Namespace(
        provisioning_server=SERVER,
        binddn="uid=Administrator,cn=users,dc=example,dc=test",
        bindpwdfile="/tmp/password",
        admin_credential_file="/etc/provisioning-secrets.json",
    )

    provider = cli._admin_password_provider(args)

    lookup.assert_not_called()
    assert provider() == "admin-secret"
    lookup.assert_called_once_with(SERVER, args.binddn, args.bindpwdfile)


def test_remote_admin_provider_requires_complete_authentication_pair(monkeypatch):
    monkeypatch.setattr(cli, "_is_local_server", lambda server: False)
    args = Namespace(
        provisioning_server=SERVER,
        binddn="uid=Administrator,cn=users,dc=example,dc=test",
        bindpwdfile=None,
        admin_credential_file="/etc/provisioning-secrets.json",
    )

    with pytest.raises(AdminCredentialError, match="Both"):
        cli._admin_password_provider(args)


def test_local_admin_provider_never_invokes_remote_transport(monkeypatch):
    local = Mock(return_value="local-admin-secret")
    remote = Mock()
    monkeypatch.setattr(cli, "_is_local_server", lambda server: True)
    monkeypatch.setattr(cli, "read_local_admin_password", local)
    monkeypatch.setattr(cli, "read_remote_admin_password", remote)
    args = Namespace(
        provisioning_server=SERVER,
        binddn="uid=Administrator,cn=users,dc=example,dc=test",
        bindpwdfile="/tmp/password",
        admin_credential_file="/custom/admin.json",
    )

    assert cli._admin_password_provider(args)() == "local-admin-secret"
    local.assert_called_once_with("/custom/admin.json")
    remote.assert_not_called()


def test_subscribe_builds_expected_objects_and_overrides_prefill(monkeypatch, tmp_path, capsys):
    captured = {}

    class FakeManager:
        def __init__(self, api, store, provider):
            captured.update(api=api, store=store, provider=provider)

        def subscribe(self, definition, *, generate_password, force):
            captured.update(definition=definition, generate_password=generate_password, force=force)
            return SubscriptionOutcome(name=definition.name, action="created")

    fake_api = SimpleNamespace(base_url="https://primary.example.test/univention/provisioning")
    monkeypatch.setattr(cli, "_api_for", lambda server, ca: fake_api)
    monkeypatch.setattr(cli, "_admin_password_provider", lambda args: lambda: "admin-secret")
    monkeypatch.setattr(cli, "SubscriptionManager", FakeManager)

    result = cli.main(subscribe_args(tmp_path, "--request-prefill", "--force"))

    assert result == 0
    assert captured["definition"].request_prefill is True
    assert captured["definition"].to_dict().keys() == {"name", "realms_topics", "request_prefill"}
    assert captured["generate_password"] is True
    assert captured["force"] is True
    assert "created" in capsys.readouterr().out


def test_unsubscribe_installs_lazy_admin_provider_without_fetching_secret(monkeypatch, tmp_path):
    provider = Mock(side_effect=AssertionError("admin secret must stay lazy on successful DELETE"))
    provider_factory = Mock(return_value=provider)

    class FakeManager:
        def __init__(self, api, store, admin_password_provider):
            assert admin_password_provider is provider

        def unsubscribe(self):
            return SubscriptionOutcome(name="ox-connector-member", action="removed")

    monkeypatch.setattr(cli, "_api_for", lambda server, ca: SimpleNamespace(base_url="https://example.test"))
    monkeypatch.setattr(cli, "_admin_password_provider", provider_factory)
    monkeypatch.setattr(cli, "SubscriptionManager", FakeManager)

    assert (
        cli.main(
            [
                "unsubscribe",
                "--subscription-file",
                str(tmp_path / "subscription.json"),
                "--provisioning-server",
                SERVER,
            ]
        )
        == 0
    )
    provider_factory.assert_called_once()
    provider.assert_not_called()


def test_unsubscribe_defaults_to_endpoint_stored_with_subscription(monkeypatch, tmp_path):
    subscription_file, _store, _record = saved_subscription(tmp_path)
    captured = {}

    class FakeManager:
        def __init__(self, api, store, admin_password_provider):
            captured.update(api=api, store=store, provider=admin_password_provider)

        def unsubscribe(self):
            return SubscriptionOutcome(name="ox-connector-member", action="removed")

    provider = Mock()
    provider_factory = Mock(return_value=provider)
    monkeypatch.setattr(cli, "_admin_password_provider", provider_factory)
    monkeypatch.setattr(cli, "SubscriptionManager", FakeManager)

    assert cli.main(["unsubscribe", "--subscription-file", str(subscription_file)]) == 0

    assert captured["api"].base_url == f"https://{BACKUP_SERVER}/univention/provisioning"
    assert provider_factory.call_args.args[0].provisioning_server == BACKUP_SERVER
    provider.assert_not_called()


def test_unsubscribe_rejects_explicit_conflicting_server_and_retains_record(monkeypatch, tmp_path, capsys):
    subscription_file, store, record = saved_subscription(tmp_path)
    manager = Mock()
    provider_factory = Mock()
    monkeypatch.setattr(cli, "SubscriptionManager", manager)
    monkeypatch.setattr(cli, "_admin_password_provider", provider_factory)

    result = cli.main(
        [
            "unsubscribe",
            "--subscription-file",
            str(subscription_file),
            "--provisioning-server",
            SERVER,
        ]
    )

    assert result == 1
    assert "does not match the endpoint stored" in capsys.readouterr().err
    assert store.load() == record
    manager.assert_not_called()
    provider_factory.assert_not_called()


def test_hidden_remote_command_prints_only_local_admin_password(monkeypatch, capsys):
    monkeypatch.setattr(cli, "read_local_admin_password", lambda: "admin-secret")

    assert cli.main(["_read-admin-password"]) == 0

    output = capsys.readouterr()
    assert output.out == "admin-secret\n"
    assert output.err == ""


def test_failure_is_redacted_and_written_to_appcenter_error_file(monkeypatch, tmp_path, capsys):
    error_file = tmp_path / "appcenter-error"
    error_file.write_text("")
    error_file.chmod(0o600)
    monkeypatch.setattr(cli, "_api_for", Mock(side_effect=ValueError("invalid safe test URL")))

    result = cli.main(subscribe_args(tmp_path, "--error-file", str(error_file)))

    assert result == 1
    assert "invalid safe test URL" in capsys.readouterr().err
    assert "invalid safe test URL" in error_file.read_text()


def test_error_file_symlink_is_not_followed(monkeypatch, tmp_path):
    target = tmp_path / "target"
    target.write_text("unchanged")
    link = tmp_path / "error-link"
    link.symlink_to(target)
    monkeypatch.setattr(cli, "_api_for", Mock(side_effect=ValueError("failure")))

    assert cli.main(subscribe_args(tmp_path, "--error-file", str(link))) == 1
    assert target.read_text() == "unchanged"


def test_force_warning_explains_queue_loss(capsys):
    cli._print_outcome("replaced", "ox-connector-member", True)

    output = capsys.readouterr()
    assert "pending event queue" in output.err
    assert "historic events" in output.err
