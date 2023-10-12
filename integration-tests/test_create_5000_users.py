import asyncio
import time

import aiohttp
import pytest
from timeit import default_timer as timer

from utils import udm_user_args

import univention.testing.strings as uts
from core.client import AsyncClient
from core.models.subscriber import FillQueueStatus


async def create_udm_users(
    user_number: int, udm_uri: str, username: str, password: str
):
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


@pytest.mark.parametrize("user_number", [1, 99, 400, 500, 1000, 3000])
@pytest.mark.asyncio
async def test_dispatcher_prefill_performance(
    udm_uri, udm_admin_username, udm_admin_password, provisioning_uri, user_number: int
):
    errors = []

    requests_per_session = 500
    user_list = [requests_per_session] * (user_number // requests_per_session)
    if remaining_requests := user_number % requests_per_session:
        user_list.append(remaining_requests)

    print(f"\ncreating {user_number} UDM users")
    dispatch_start = timer()
    tasks = []
    for users in user_list:
        tasks.append(
            create_udm_users(users, udm_uri, udm_admin_username, udm_admin_password)
        )

    results = await asyncio.gather(*tasks)
    errors = [error for result in results for error in result]

    if errors:
        print(
            f"encountered {len(errors)} during user creation, showing the 5 latest errors:"
        )
        print(errors[:5])
    assert not errors

    subscription_name = uts.random_string()

    provisioning_client = AsyncClient(provisioning_uri)
    await provisioning_client.create_subscription(
        subscription_name, [["udm", "users/user"]], fill_queue=True
    )

    print("Waiting for pre-filling")
    dispatch_start = timer()
    status = FillQueueStatus.running
    while status == FillQueueStatus.running:
        response = await provisioning_client.get_subscription(subscription_name)
        status = response.fill_queue_status
        time.sleep(1)
    dispatch_end = timer()
    prefill_wait = dispatch_end - dispatch_start

    messages = await provisioning_client.get_subscription_messages(
        subscription_name, count=100_000
    )

    print(f"pre-filled {len(messages)} in {prefill_wait} Seconds\n")
    # print(messages[-1])
    assert messages
