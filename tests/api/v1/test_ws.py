# import uuid
# from typing import Optional
#
# from fakeredis.aioredis import FakeRedis
# from fastapi.testclient import TestClient
#
# from consumer.messages.api import v1_prefix as messages_api_prefix
# from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
# from consumer.main import app
#
#
# class RedisXreadMock:
#     async def xread_1(
#         self,
#         streams,
#         count: Optional[int] = None,
#         block: Optional[int] = None,
#     ):
#         stream = list(streams.keys())[0]
#         return {
#             stream: [
#                 [
#                     (
#                         "1696253842318-0",
#                         {
#                             "publisher_name": "testclient",
#                             "ts": "2023-10-02T13:37:22.314397",
#                             "realm": "foo",
#                             "topic": "bar/baz",
#                             "body": '{"first": {"foo": "1"}}',
#                         },
#                     )
#                 ]
#             ]
#         }
#
#     async def xread_2(
#         self,
#         streams,
#         count: Optional[int] = None,
#         block: Optional[int] = None,
#     ):
#         stream = list(streams.keys())[0]
#         return {
#             stream: [
#                 [
#                     (
#                         "1696253842318-0",
#                         {
#                             "publisher_name": "testclient",
#                             "ts": "2023-10-02T13:37:22.314397",
#                             "realm": "foo",
#                             "topic": "bar/baz",
#                             "body": '{"second": {"bar": "2"}}',
#                         },
#                     )
#                 ]
#             ]
#         }
#
#
# def test_websocket(monkeypatch):
#     client = TestClient(app)
#     name = str(uuid.uuid4())
#     realm = "foo"
#     topic = "bar/baz"
#     body1 = {"first": {"foo": "1"}}
#     body2 = {"second": {"bar": "2"}}
#
#     response = client.post(
#         f"{subscriptions_api_prefix}/subscription/",
#         json={
#             "name": name,
#             "realms_topics": [[realm, topic]],
#             "fill_queue": False,
#         },
#     )
#     assert response.status_code == 201
#
#     response = client.post(
#         f"{messages_api_prefix}/message/",
#         json={
#             "realm": realm,
#             "topic": topic,
#             "body": body1,
#         },
#     )
#     assert response.status_code == 202
#
#     response = client.post(
#         f"{messages_api_prefix}/message/",
#         json={
#             "realm": realm,
#             "topic": topic,
#             "body": body2,
#         },
#     )
#     assert response.status_code == 202
#
#     monkeypatch.setattr(FakeRedis, "xread", RedisXreadMock.xread_1)
#     with client.websocket_connect(
#         f"{messages_api_prefix}/subscription/{name}/ws"
#     ) as ws_client:
#         data = ws_client.receive_json()
#
#         assert data["realm"] == realm
#         assert data["topic"] == topic
#         assert data["body"] == body1
#
#         monkeypatch.setattr(FakeRedis, "xread", RedisXreadMock.xread_2)
#         ws_client.send_json({"status": "ok"})
#
#         data = ws_client.receive_json()
#         assert data["realm"] == realm
#         assert data["topic"] == topic
#         assert data["body"] == body2
