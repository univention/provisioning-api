# import uuid
#
# import httpx
# import pytest
#
# from core.models.subscriber import FillQueueStatus
# from consumer.subscriptions.api import v1_prefix as api_prefix
# from consumer.main import app
#
#
# @pytest.fixture(scope="session")
# def anyio_backend():
#     return "asyncio"
#
#
# @pytest.fixture(scope="session")
# async def client():
#     async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
#         yield client
#
#
# @pytest.mark.anyio
# async def test_create_and_get_subscription(client: httpx.AsyncClient):
#     name = str(uuid.uuid4())
#     realms_topics = [
#         ["foo", "bar/baz"],
#         ["abc", "def/ghi"],
#     ]
#
#     response = await client.post(
#         f"{api_prefix}/subscription/",
#         json={
#             "name": name,
#             "realms_topics": realms_topics,
#             "fill_queue": False,
#         },
#     )
#     assert response.status_code == 201
#
#     response = await client.get(f"{api_prefix}/subscription/{name}")
#     assert response.status_code == 200
#     data = response.json()
#
#     assert data["name"] == name
#     assert not data["fill_queue"]
#     assert data["fill_queue_status"] == FillQueueStatus.done
#     assert len(data["realms_topics"]) == len(realms_topics)
#     assert all(
#         ([realm, topic] in data["realms_topics"] for realm, topic in realms_topics)
#     )
#
#
# @pytest.mark.anyio
# async def test_get_subscriptions(client: httpx.AsyncClient):
#     subscriptions = [
#         {
#             "name": str(uuid.uuid4()),
#             "realms_topics": [
#                 ["foo", "bar/baz"],
#                 ["abc", "def/ghi"],
#             ],
#         },
#         {
#             "name": str(uuid.uuid4()),
#             "realms_topics": [
#                 ["foo", "f33d/f00d"],
#                 ["bar", "c0ff/ee"],
#             ],
#         },
#     ]
#
#     for sub in subscriptions:
#         response = await client.post(
#             f"{api_prefix}/subscription/",
#             json={
#                 "name": sub["name"],
#                 "realms_topics": sub["realms_topics"],
#                 "fill_queue": False,
#             },
#         )
#         assert response.status_code == 201
#
#     response = await client.get(f"{api_prefix}/subscription/")
#     assert response.status_code == 200
#     data = response.json()
#
#     for request in subscriptions:
#         ok = False
#         for returned in data:
#             if returned["name"] != request["name"]:
#                 continue
#
#             assert len(returned["realms_topics"]) == len(request["realms_topics"])
#             assert all(
#                 (
#                     [realm, topic] in returned["realms_topics"]
#                     for realm, topic in request["realms_topics"]
#                 )
#             )
#
#             ok = True
#
#         assert ok
#
#
# @pytest.mark.anyio
# async def test_delete_subscription(client: httpx.AsyncClient):
#     name = str(uuid.uuid4())
#     realms_topics = [
#         ["foo", "bar/baz"],
#         ["abc", "def/ghi"],
#     ]
#
#     response = await client.post(
#         f"{api_prefix}/subscription/",
#         json={
#             "name": name,
#             "realms_topics": realms_topics,
#             "fill_queue": False,
#         },
#     )
#     assert response.status_code == 201
#
#     response = await client.get(f"{api_prefix}/subscription/{name}")
#     assert response.status_code == 200
#     assert response.json()["name"] == name
#
#     response = await client.delete(f"{api_prefix}/subscription/{name}")
#     assert response.status_code == 200
#
#     response = await client.get(f"{api_prefix}/subscription/{name}")
#     assert response.status_code == 404
