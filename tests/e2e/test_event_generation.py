# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import pytest

from univention.admin.rest.client import UDM


@pytest.fixture(scope="function")
def maildomain(udm):
    name = "ldif-producer.unittests"
    domains = udm.get("mail/domain")
    maildomain = domains.new()
    maildomain.properties.update({"name": name})
    maildomain.save()
    yield name
    maildomain.delete()


@pytest.mark.timeout(10)
def test_create_delete_maildomain(maildomain):
    assert maildomain


@pytest.mark.timeout(30)
def test_create_delete_user(udm: UDM, maildomain):
    users = udm.get("users/user")
    assert users
    user = users.new()
    username = str(uuid.uuid1())
    user.properties.update(
        {
            "username": username,
            "firstname": "test_event_generation",
            "lastname": username,
            "password": "univention",
            "mailPrimaryAddress": f"{username}@{maildomain}",
        }
    )
    user.save()
    user.delete()


# Only works after stack-data
@pytest.mark.skip
def test_create_accessprofile(udm: UDM):
    accessprofile = udm.get("oxmail/accessprofile")
    assert accessprofile
    profile = accessprofile.new()
    name = str(uuid.uuid1())

    profile.properties.update({"name": name, "displayName": name})

    profile.save()
    profile.delete()


# Only works after stack-data
@pytest.mark.skip
def test_create_functional_account(udm: UDM, maildomain):
    accessprofile = udm.get("oxmail/functional_account")
    assert accessprofile
    account = accessprofile.new()
    name = str(uuid.uuid1())

    account.properties.update(
        {"name": name, "mailPrimaryAddress": f"{name}@{maildomain}"}
    )

    account.save()
    account.delete()
