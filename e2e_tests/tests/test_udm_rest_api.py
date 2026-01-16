
import time
import uuid

import pytest

from univention.admin.rest.client import UDM


@pytest.fixture
def udm_rest_1_connection(test_settings):
    udm = UDM(
        "localhost:9980/udm/",
        test_settings.udm_rest_api_username,
        test_settings.udm_rest_api_password,
    )
    # test the connection
    udm.get_ldap_base()
    return udm


def test_udm_rest_reload(create_extended_attribute, udm_rest_1_connection, test_settings):

    extended_attribute, cli_name = create_extended_attribute
    time.sleep(5)

    base_properties = {
        "username": str(uuid.uuid1()),
        "firstname": "John",
        "lastname": "Doe",
        "password": "password",
        "pwdChangeNextLogin": True,
    }
    properties = {**base_properties, **({cli_name: "test@univention.de"})}

    # Create user directly via HTTP POST to avoid triggering reload
    import requests
    from requests.auth import HTTPBasicAuth

    url = f"http://localhost:9980/udm/users/user/"
    auth = HTTPBasicAuth(
        test_settings.udm_rest_api_username,
        test_settings.udm_rest_api_password
    )

    response = requests.post(
        url,
        json={
            "position": f"cn=users,{udm_rest_1_connection.get_ldap_base()}",
            "properties": properties
        },
        auth=auth
    )

    assert response.status_code == 201, f"Failed to create user: {response.text}"
    user_data = response.json()
    user_dn = user_data["dn"]
    print(f"Created user with DN: {user_dn}")

    # Verify the extended attribute is set in the create response
    user_properties = user_data["properties"]
    assert cli_name in user_properties, f"Extended attribute '{cli_name}' not found in user properties"
    assert user_properties[cli_name] == "test@univention.de", \
        f"Expected extended attribute '{cli_name}' to be 'test@univention.de', got '{user_properties[cli_name]}'"
    print(f"Verified extended attribute '{cli_name}' is set to: {user_properties[cli_name]}")

    # Cleanup
    requests.delete(f"http://localhost:9980/udm/users/user/{user_dn}", auth=auth)

