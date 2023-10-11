import pytest
from univention.admin.rest.client import UDM

from utils import udm_user_args


@pytest.mark.parametrize("user_number", [100])
def test_udm_connection(udm: UDM, user_number: int):
    users_user = udm.get("users/user")
    users = []

    for _ in range(user_number):
        test_user = users_user.new()
        user_args = udm_user_args(minimal=False)
        test_user.properties.update(user_args)
        test_user.save()
        users.append(test_user.dn)
