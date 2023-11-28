import json
from typing import List, Optional

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
        realms_topics: List[List[str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        sub_info = {
            "name": name,
            "realms_topics": realms_topics,
            "fill_queue": int(fill_queue),
            "fill_queue_status": fill_queue_status,
        }
        await self.kv_store.put(
            NatsKeys.subscriber(name), json.dumps(sub_info).encode("utf-8")
        )
        await self.update_subscribers_for_key(NatsKeys.subscribers, name)

        for realm, topic in realms_topics:
            await self.update_subscribers_for_key(f"{realm}:{topic}", name)

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        try:
            sub = await self.kv_store.get(NatsKeys.subscriber(name))
            return json.loads(sub.value.decode("utf-8"))
        except KeyNotFoundError:
            return None

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        await self.kv_store.put(
            NatsKeys.subscriber(name), json.dumps(sub_info).encode("utf-8")
        )

    async def delete_subscriber_from_key(self, key: str, name: str):
        subs = await self.get_subscribers_for_key(key)
        subs.remove(name)
        if not subs:
            await self.kv_store.delete(key)
        else:
            await self.kv_store.put(key, ",".join(subs).encode("utf-8"))

    async def delete_subscriber(self, name: str):
        await self.delete_subscriber_from_key(NatsKeys.subscribers, name)

        sub_info = await self.get_subscriber_info(name)
        realms_topics = sub_info["realms_topics"]

        for realm, topic in realms_topics:
            await self.delete_subscriber_from_key(f"{realm}:{topic}", name)

        await self.kv_store.delete(NatsKeys.subscriber(name))

    async def get_subscribers_for_key(self, key: str):
        try:
            names = await self.kv_store.get(key)
            return names.value.decode("utf-8").split(",")
        except KeyNotFoundError:
            return []

    async def update_subscribers_for_key(self, key: str, name: str) -> None:
        try:
            subs = await self.kv_store.get(key)
            updated_subs = subs.value.decode("utf-8") + f",{name}"
            await self.kv_store.put(key, updated_subs.encode("utf-8"))
        except KeyNotFoundError:
            await self.kv_store.put(key, name.encode("utf-8"))
