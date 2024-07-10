# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
from pprint import pprint

import pytest

from univention.admin.rest.client import UDM, BadRequest


@pytest.fixture(scope="function")
def maildomain(udm):
    name = f"ldif-producer.unittests.{str(uuid.uuid1())}"
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
def test_create_user(udm: UDM, maildomain):
    users = udm.get("users/user")
    assert users

    errors = []
    unknown_errors = []

    for i in range(200):
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

        try:
            user.save()
        except BadRequest as err:
            errors.append((i, err.error_details))
        except Exception as err:
            unknown_errors.append((i, err))

    pprint(errors)
    pprint(unknown_errors)
    assert not errors
    assert not unknown_errors


def test_create_delete_user(udm: UDM, maildomain):
    users = udm.get("users/user")
    assert users

    errors = []
    unknown_errors = []

    for i in range(200):
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
        try:
            user.save()
            user.delete()
        except BadRequest as err:
            errors.append((i, err.error_details))
        except Exception as err:
            unknown_errors.append((i, err))

    pprint(errors)
    pprint(unknown_errors)
    assert not errors
    assert not unknown_errors


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
