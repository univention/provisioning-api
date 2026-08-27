# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import bcrypt
import pytest

from univention.provisioning.rest.subscription_service import hash_password, verify_password


@pytest.fixture(autouse=True)
def _clear_password_cache():
    verify_password.cache.clear()
    yield
    verify_password.cache.clear()


def test_hash_password_roundtrip():
    assert verify_password("s3cret", hash_password("s3cret")) is True


def test_hash_password_rejects_wrong_password():
    assert verify_password("wrong", hash_password("s3cret")) is False


def test_hash_password_keeps_the_passlib_format():
    ident, cost = hash_password("s3cret").split("$")[1:3]
    assert ident == "2b"
    assert cost == "12"


def test_hash_password_salts():
    assert hash_password("s3cret") != hash_password("s3cret")


@pytest.mark.parametrize("prefix", [b"2a", b"2b"])
def test_verify_password_accepts_hashes_written_by_passlib(prefix):
    stored = bcrypt.hashpw(b"s3cret", bcrypt.gensalt(prefix=prefix)).decode("ASCII")
    assert verify_password("s3cret", stored) is True


def test_verify_password_accepts_a_lower_cost_hash():
    stored = bcrypt.hashpw(b"s3cret", bcrypt.gensalt(rounds=4)).decode("ASCII")
    assert verify_password("s3cret", stored) is True


def test_password_longer_than_the_bcrypt_limit_is_truncated():
    """bcrypt ignores everything past 72 bytes, and so did passlib."""
    stored = hash_password("x" * 100)
    assert verify_password("x" * 72, stored) is True


def test_non_ascii_passwords():
    assert verify_password("pässwörd-日本", hash_password("pässwörd-日本")) is True
