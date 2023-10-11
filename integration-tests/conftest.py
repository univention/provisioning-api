import os
import pytest

from univention.admin.rest.client import UDM


@pytest.fixture
def udm_uri():
    # cannot verify https in the container at the moment
    return os.environ.get(
        "TESTS_UDM_ADMIN_URL", "http://localhost:8000/univention/udm/"
    )


@pytest.fixture
def udm_admin_username():
    return os.environ.get("TESTS_UDM_ADMIN_USERNAME", "Administrator")


@pytest.fixture
def udm_admin_password():
    return os.environ.get("TESTS_UDM_ADMIN_PASSWORD", "univention")


@pytest.fixture
def udm(udm_uri, udm_admin_username, udm_admin_password):
    udm = UDM(udm_uri, udm_admin_username, udm_admin_password)
    # test the connection
    udm.get_ldap_base()
    return udm
