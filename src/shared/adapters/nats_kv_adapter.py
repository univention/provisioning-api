import json
from typing import List, Union, Optional

from nats.aio.client import Client as NATS
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue

from shared.adapters.nats_adapter import NatsKeys


class NatsKVAdapter:
    def __init__(self):
        self.nats = NATS()
        self.js = self.nats.jetstream()
        self.kv_store: Optional[KeyValue] = None

    async def connect(self, servers: List[str]):
        await self.nats.connect(servers=servers)

    async def close(self):
        await self.nats.close()

    async def create_kv_store(self, name: str):
        self.kv_store = await self.js.create_key_value(bucket=name)

    async def add_subscriber(
        self,
        name: str,
        realm_topic: str,
        fill_queue: bool,
        fill_queue_status: str,
    ):
        sub_info = {
            "name": name,
            "realms_topics": [realm_topic],
            "fill_queue": int(fill_queue),
            "fill_queue_status": fill_queue_status,
        }
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)
        await self.update_subscribers_for_key(NatsKeys.subscribers, name)

        await self.update_subscribers_for_key(realm_topic, name)

    async def create_subscription(self, name: str, realm_topic: str, sub_info: dict):
        sub_info["realms_topics"].append(realm_topic)
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)
        await self.update_subscribers_for_key(realm_topic, name)

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        try:
            sub = await self.kv_store.get(NatsKeys.subscriber(name))
            return json.loads(sub.value.decode("utf-8"))
        except KeyNotFoundError:
            return None

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)

    async def delete_subscriber_from_key(self, key: str, name: str):
        subs = await self.get_subscribers_for_key(key)
        subs.remove(name)
        if not subs:
            await self.kv_store.delete(key)
        else:
            await self.put_value_by_key(key, ",".join(subs))

    async def delete_subscriber(self, name: str):
        await self.delete_subscriber_from_key(NatsKeys.subscribers, name)
        await self.kv_store.delete(NatsKeys.subscriber(name))

    async def get_value_by_key(self, key: str) -> Optional[KeyValue.Entry]:
        try:
            return await self.kv_store.get(key)
        except KeyNotFoundError:
            return None

    async def put_value_by_key(self, key: str, value: Union[str, dict]):
        if isinstance(value, dict):
            value = json.dumps(value)
        await self.kv_store.put(key, value.encode("utf-8"))

    async def get_subscribers_for_key(self, key: str):
        names = await self.get_value_by_key(key)
        return names.value.decode("utf-8").split(",") if names else []

    async def update_subscribers_for_key(self, key: str, name: str) -> None:
        try:
            subs = await self.kv_store.get(key)
            updated_subs = subs.value.decode("utf-8") + f",{name}"
            await self.put_value_by_key(key, updated_subs)
        except KeyNotFoundError:
            await self.put_value_by_key(key, name)
