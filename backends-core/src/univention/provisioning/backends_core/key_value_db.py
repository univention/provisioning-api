# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Protocol, runtime_checkable

from univention.provisioning.backends_core.constants import BucketName


class UpdateConflict(Exception): ...


@runtime_checkable
class KeyValueDB(Protocol):
    async def init(self, buckets: list[BucketName]) -> None: ...

    async def close(self) -> None: ...

    async def get_value(self, key: str, bucket: BucketName) -> str | None: ...

    async def get_value_with_revision(self, key: str, bucket: BucketName) -> tuple[str, int | None] | None: ...

    async def put_value(
        self,
        key: str,
        value: str | dict | list,
        bucket: BucketName,
        revision: int | None = None,
    ) -> None: ...
