# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Secure, crash-resistant storage for limited subscriber credentials."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from .models import DefinitionError, SubscriptionDefinition

SCHEMA_VERSION = 1
DEFAULT_MAX_BYTES = 64 * 1024
_RECORD_KEYS = frozenset({"schema_version", "state", "provisioning_api_base_url", "subscription", "password"})
_REPLACEMENT_AUTHORIZATION_KEY = "replacement_authorized"


class StorageError(RuntimeError):
    """A subscriber credential file could not be handled safely."""


def _validate_base_url(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 2048 or any(ord(character) < 32 for character in value):
        raise StorageError("provisioning API base URL is invalid")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise StorageError("provisioning API base URL is invalid") from exc
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or port is not None
        and not 1 <= port <= 65535
    ):
        raise StorageError("provisioning API base URL must be an HTTPS URL without credentials, query, or fragment")
    return value


def _validate_password(value: Any) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 4096
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise StorageError("subscriber password is invalid")
    return value


@dataclass(frozen=True, slots=True)
class SubscriptionRecord:
    """One candidate or active subscription and its limited password."""

    state: Literal["candidate", "active"]
    base_url: str
    definition: SubscriptionDefinition
    password: str
    replacement_authorized: bool = False

    def __post_init__(self) -> None:
        if self.state not in ("candidate", "active"):
            raise StorageError("subscription record state must be candidate or active")
        _validate_base_url(self.base_url)
        if not isinstance(self.definition, SubscriptionDefinition):
            raise StorageError("subscription record definition is invalid")
        _validate_password(self.password)
        if type(self.replacement_authorized) is not bool:
            raise StorageError("subscription replacement authorization must be a boolean")
        if self.state == "active" and self.replacement_authorized:
            raise StorageError("an active subscription cannot retain replacement authorization")

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def provisioning_api_base_url(self) -> str:
        return self.base_url

    @classmethod
    def candidate(
        cls,
        *,
        base_url: str,
        definition: SubscriptionDefinition,
        password: str,
        replacement_authorized: bool = False,
    ) -> SubscriptionRecord:
        return cls(
            state="candidate",
            base_url=base_url,
            definition=definition,
            password=password,
            replacement_authorized=replacement_authorized,
        )

    def authorize_replacement(self) -> SubscriptionRecord:
        if self.state != "candidate":
            raise StorageError("replacement authorization can be persisted only for a candidate subscription")
        return replace(self, replacement_authorized=True)

    def activate(self) -> SubscriptionRecord:
        return replace(self, state="active", replacement_authorized=False)

    @classmethod
    def from_mapping(cls, value: object) -> SubscriptionRecord:
        if not isinstance(value, Mapping):
            raise StorageError("subscription credential file has an invalid structure")
        keys = set(value)
        if keys not in (_RECORD_KEYS, _RECORD_KEYS | {_REPLACEMENT_AUTHORIZATION_KEY}):
            raise StorageError("subscription credential file has an invalid structure")
        if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
            raise StorageError("subscription credential file has an unsupported schema version")
        try:
            definition = SubscriptionDefinition.from_mapping(value["subscription"])
        except DefinitionError as exc:
            raise StorageError("subscription credential file contains an invalid definition") from exc
        return cls(
            state=value["state"],
            base_url=value["provisioning_api_base_url"],
            definition=definition,
            password=value["password"],
            replacement_authorized=value.get(_REPLACEMENT_AUTHORIZATION_KEY, False),
        )

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "state": self.state,
            "provisioning_api_base_url": self.base_url,
            "subscription": self.definition.to_dict(),
            "password": self.password,
        }
        if self.replacement_authorized:
            value[_REPLACEMENT_AUTHORIZATION_KEY] = True
        return value

    def __repr__(self) -> str:
        return (
            f"SubscriptionRecord(state={self.state!r}, base_url={self.base_url!r}, "
            f"definition={self.definition!r}, password=<redacted>, "
            f"replacement_authorized={self.replacement_authorized!r})"
        )


class SubscriptionStore:
    """Read and atomically update one protected subscription file."""

    def __init__(self, path: str | os.PathLike[str], *, max_bytes: int = DEFAULT_MAX_BYTES) -> None:
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.path = Path(path)
        self.max_bytes = max_bytes

    def load(self) -> SubscriptionRecord | None:
        """Load a protected file, returning ``None`` when it does not exist."""

        directory_fd = self._open_directory(create=False)
        if directory_fd is None:
            return None
        try:
            try:
                file_fd = os.open(
                    self.path.name,
                    os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW,
                    dir_fd=directory_fd,
                )
            except FileNotFoundError:
                return None
            except OSError as exc:
                raise StorageError("subscription credential file cannot be opened safely") from exc

            try:
                metadata = os.fstat(file_fd)
                self._validate_file_metadata(metadata)
                raw = self._read_bounded(file_fd, metadata.st_size)
            finally:
                os.close(file_fd)
        finally:
            os.close(directory_fd)

        try:
            decoded = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
            raise StorageError("subscription credential file is not valid JSON") from exc
        return SubscriptionRecord.from_mapping(decoded)

    def save(self, record: SubscriptionRecord) -> None:
        """Atomically write a candidate or active record with mode ``0600``."""

        if not isinstance(record, SubscriptionRecord):
            raise TypeError("record must be a SubscriptionRecord")
        raw = (json.dumps(record.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
        if len(raw) > self.max_bytes:
            raise StorageError("subscription credential record is too large")

        directory_fd = self._open_directory(create=True)
        assert directory_fd is not None
        temporary_path: str | None = None
        try:
            self._validate_existing_target(directory_fd)
            file_fd, temporary_path = tempfile.mkstemp(
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                dir=self.path.parent,
            )
            try:
                os.fchmod(file_fd, 0o600)
                view = memoryview(raw)
                while view:
                    written = os.write(file_fd, view)
                    if written <= 0:
                        raise StorageError("failed to write subscription credential file")
                    view = view[written:]
                os.fsync(file_fd)
            finally:
                os.close(file_fd)

            os.replace(temporary_path, self.path.name, dst_dir_fd=directory_fd)
            temporary_path = None
            os.fsync(directory_fd)
        except StorageError:
            raise
        except OSError as exc:
            raise StorageError("subscription credential file could not be saved") from exc
        finally:
            if temporary_path is not None:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
            os.close(directory_fd)

    def delete(self) -> bool:
        """Delete a safe regular credential file and fsync its directory."""

        directory_fd = self._open_directory(create=False)
        if directory_fd is None:
            return False
        try:
            try:
                metadata = os.stat(self.path.name, dir_fd=directory_fd, follow_symlinks=False)
            except FileNotFoundError:
                return False
            self._validate_file_metadata(metadata)
            try:
                os.unlink(self.path.name, dir_fd=directory_fd)
                os.fsync(directory_fd)
            except OSError as exc:
                raise StorageError("subscription credential file could not be deleted") from exc
            return True
        finally:
            os.close(directory_fd)

    def _open_directory(self, *, create: bool) -> int | None:
        try:
            return self._validated_directory_fd()
        except FileNotFoundError:
            if not create:
                return None
        try:
            os.mkdir(self.path.parent, mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise StorageError("subscription credential directory could not be created") from exc
        try:
            return self._validated_directory_fd()
        except OSError as exc:
            raise StorageError("subscription credential directory cannot be opened safely") from exc

    def _validated_directory_fd(self) -> int:
        flags = os.O_RDONLY | os.O_CLOEXEC | os.O_DIRECTORY | os.O_NOFOLLOW
        try:
            directory_fd = os.open(self.path.parent, flags)
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise StorageError("subscription credential directory cannot be opened safely") from exc
        metadata = os.fstat(directory_fd)
        if metadata.st_uid != os.geteuid() or stat.S_IMODE(metadata.st_mode) != 0o700:
            os.close(directory_fd)
            raise StorageError("subscription credential directory must be owned by the current user with mode 0700")
        return directory_fd

    def _validate_existing_target(self, directory_fd: int) -> None:
        try:
            metadata = os.stat(self.path.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        self._validate_file_metadata(metadata)

    @staticmethod
    def _validate_file_metadata(metadata: os.stat_result) -> None:
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise StorageError("subscription credential path must be one regular, non-linked file")
        if metadata.st_uid != os.geteuid():
            raise StorageError("subscription credential file must be owned by the current user")
        if stat.S_IMODE(metadata.st_mode) != 0o600:
            raise StorageError("subscription credential file must have mode 0600")

    def _read_bounded(self, file_fd: int, reported_size: int) -> bytes:
        if reported_size > self.max_bytes:
            raise StorageError("subscription credential file is too large")
        chunks: list[bytes] = []
        remaining = self.max_bytes + 1
        while remaining:
            chunk = os.read(file_fd, min(remaining, 8192))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > self.max_bytes:
            raise StorageError("subscription credential file is too large")
        return raw
