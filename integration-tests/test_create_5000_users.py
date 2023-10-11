import aiohttp
import pytest

from utils import udm_user_args


async def create_udm_users(user_number: int):
    errors = []

    auth = aiohttp.BasicAuth("Administrator", "univention")
    headers = {"Accept": "application/json"}

    async with aiohttp.ClientSession(auth=auth, headers=headers) as session:
        response = await session.get(
            "http://localhost:8000/univention/udm/users/user/add"
        )
        test_user = await response.json()

        for _ in range(user_number):
            user_args = udm_user_args(minimal=False)
            test_user["properties"].update(user_args)
            response = await session.post(
                "http://localhost:8000/univention/udm/users/user/", json=test_user
            )
            if not response.status == 201:
                errors.append(await response.json())
    return errors


@pytest.mark.parametrize("user_number", [1, 1000])  # [1, 10, 50, 100])
@pytest.mark.asyncio
async def test_udm_connection(user_number: int):
    errors = []

    requests_per_session = 100
    sessions = [requests_per_session] * (user_number // requests_per_session)
    if remaining_requests := user_number % requests_per_session:
        sessions.append(remaining_requests)

    for session in sessions:
        errors.extend(await create_udm_users(session))

    print(errors[:5])
    assert not errors
