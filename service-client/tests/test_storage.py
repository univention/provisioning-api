# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import json
import os
import stat
from pathlib import Path

import pytest

from univention.provisioning.service_client.models import RealmTopic, SubscriptionDefinition
from univention.provisioning.service_client.storage import StorageError, SubscriptionRecord, SubscriptionStore


@pytest.fixture
def definition() -> SubscriptionDefinition:
    return SubscriptionDefinition(
        name="ox-connector-ucs-3220",
        realms_topics=(RealmTopic(realm="users", topic="user"),),
        request_prefill=True,
    )


@pytest.fixture
def candidate(definition: SubscriptionDefinition) -> SubscriptionRecord:
    return SubscriptionRecord.candidate(
        base_url="https://primary.example.test/univention/provisioning/",
        definition=definition,
        password="limited-subscriber-secret",
    )


def make_store(tmp_path: Path, **kwargs: object) -> SubscriptionStore:
    return SubscriptionStore(tmp_path / "secrets" / "provisioning-subscription.json", **kwargs)


def write_raw(store: SubscriptionStore, raw: bytes, *, mode: int = 0o600) -> None:
    store.path.parent.mkdir(mode=0o700)
    store.path.write_bytes(raw)
    store.path.chmod(mode)


def test_save_load_activate_and_delete(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)

    assert store.load() is None
    store.save(candidate)

    assert stat.S_IMODE(store.path.parent.stat().st_mode) == 0o700
    assert stat.S_IMODE(store.path.stat().st_mode) == 0o600
    assert store.load() == candidate
    assert store.load().name == "ox-connector-ucs-3220"  # type: ignore[union-attr]
    assert store.load().provisioning_api_base_url == candidate.base_url  # type: ignore[union-attr]

    active = candidate.activate()
    store.save(active)
    assert store.load() == active
    assert store.delete() is True
    assert store.load() is None
    assert store.delete() is False


def test_json_file_has_stable_versioned_shape(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)

    store.save(candidate)

    assert json.loads(store.path.read_text()) == {
        "schema_version": 1,
        "state": "candidate",
        "provisioning_api_base_url": "https://primary.example.test/univention/provisioning/",
        "subscription": {
            "name": "ox-connector-ucs-3220",
            "realms_topics": [{"realm": "users", "topic": "user"}],
            "request_prefill": True,
        },
        "password": "limited-subscriber-secret",
    }


def test_force_authorization_is_candidate_only_and_cleared_on_activation(
    tmp_path: Path,
    candidate: SubscriptionRecord,
) -> None:
    store = make_store(tmp_path)
    authorized = candidate.authorize_replacement()

    store.save(authorized)

    assert store.load() == authorized
    assert json.loads(store.path.read_text())["replacement_authorized"] is True

    active = authorized.activate()
    store.save(active)

    assert active.replacement_authorized is False
    assert "replacement_authorized" not in json.loads(store.path.read_text())


def test_existing_v1_file_without_force_authorization_remains_compatible(
    tmp_path: Path,
    candidate: SubscriptionRecord,
) -> None:
    store = make_store(tmp_path)
    legacy_value = candidate.to_dict()
    assert "replacement_authorized" not in legacy_value
    write_raw(store, json.dumps(legacy_value).encode())

    loaded = store.load()

    assert loaded == candidate
    assert loaded is not None
    assert loaded.replacement_authorized is False


def test_active_file_cannot_claim_force_authorization(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    invalid = candidate.activate().to_dict()
    invalid["replacement_authorized"] = True
    write_raw(store, json.dumps(invalid).encode())

    with pytest.raises(StorageError, match="active subscription"):
        store.load()


def test_record_repr_and_validation_errors_do_not_leak_password(
    candidate: SubscriptionRecord, definition: SubscriptionDefinition
) -> None:
    assert "limited-subscriber-secret" not in repr(candidate)
    assert "<redacted>" in repr(candidate)

    with pytest.raises(StorageError) as error:
        SubscriptionRecord(
            state="broken",  # type: ignore[arg-type]
            base_url="https://primary.example.test/",
            definition=definition,
            password="another-secret",
        )
    assert "another-secret" not in str(error.value)


@pytest.mark.parametrize(
    "raw",
    [
        b"not JSON",
        b"[]",
        json.dumps({"schema_version": 99}).encode(),
        json.dumps(
            {
                "schema_version": 1,
                "state": "candidate",
                "provisioning_api_base_url": "https://primary.example.test/",
                "subscription": {
                    "name": "bad name",
                    "realms_topics": [{"realm": "users", "topic": "user"}],
                    "request_prefill": True,
                },
                "password": "do-not-leak",
            }
        ).encode(),
    ],
)
def test_malformed_file_is_rejected_without_content_in_error(tmp_path: Path, raw: bytes) -> None:
    store = make_store(tmp_path)
    write_raw(store, raw)

    with pytest.raises(StorageError) as error:
        store.load()
    assert "do-not-leak" not in str(error.value)


def test_load_rejects_oversized_file(tmp_path: Path) -> None:
    store = make_store(tmp_path, max_bytes=32)
    write_raw(store, b"x" * 33)

    with pytest.raises(StorageError, match="too large"):
        store.load()


def test_load_and_save_reject_wrong_file_permissions(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    write_raw(store, b"{}", mode=0o640)

    with pytest.raises(StorageError, match="0600"):
        store.load()
    with pytest.raises(StorageError, match="0600"):
        store.save(candidate)


def test_store_rejects_wrong_directory_permissions(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    store.path.parent.mkdir(mode=0o755)

    with pytest.raises(StorageError, match="0700"):
        store.save(candidate)


def test_symlink_is_never_followed_or_deleted(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    store.path.parent.mkdir(mode=0o700)
    target = tmp_path / "target"
    target.write_text("must survive")
    store.path.symlink_to(target)

    with pytest.raises(StorageError):
        store.load()
    with pytest.raises(StorageError):
        store.save(candidate)
    with pytest.raises(StorageError):
        store.delete()
    assert store.path.is_symlink()
    assert target.read_text() == "must survive"


def test_non_regular_target_is_not_deleted(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.path.parent.mkdir(mode=0o700)
    store.path.mkdir()

    with pytest.raises(StorageError, match="regular"):
        store.delete()
    assert store.path.is_dir()


def test_hard_linked_file_is_rejected(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    store.save(candidate)
    os.link(store.path, tmp_path / "second-link")

    with pytest.raises(StorageError, match="non-linked"):
        store.load()


def test_replacement_is_atomic_and_leaves_no_temporary_files(tmp_path: Path, candidate: SubscriptionRecord) -> None:
    store = make_store(tmp_path)
    store.save(candidate)
    old_inode = store.path.stat().st_ino

    store.save(candidate.activate())

    assert store.path.stat().st_ino != old_inode
    assert store.load() == candidate.activate()
    assert list(store.path.parent.glob(f".{store.path.name}.*.tmp")) == []


def test_failed_replace_preserves_old_file_and_cleans_temporary_file(
    tmp_path: Path, candidate: SubscriptionRecord, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = make_store(tmp_path)
    store.save(candidate)
    original = store.path.read_bytes()

    def fail_replace(*args: object, **kwargs: object) -> None:
        raise OSError("simulated failure")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(StorageError, match="could not be saved"):
        store.save(candidate.activate())
    assert store.path.read_bytes() == original
    assert list(store.path.parent.glob(f".{store.path.name}.*.tmp")) == []
