from typing import List, Union, Optional


class KVStoreAdapter:
    def __init__(self, kv_store):
        self.kv_store = kv_store

    async def connect(self, servers: List[str]):
        await self.kv_store.connect(servers=servers)

    async def close(self):
        await self.kv_store.close()

    async def create_kv_store(self, name: str = "Pub_Sub_KV"):
        await self.kv_store.create_kv_store(name=name)

    async def add_subscriber(
        self,
        name: str,
        realm_topic: str,
        fill_queue: bool,
        fill_queue_status: str,
    ):
        await self.kv_store.add_subscriber(
            name=name,
            realm_topic=realm_topic,
            fill_queue=fill_queue,
            fill_queue_status=fill_queue_status,
        )

    async def create_subscription(self, name: str, realm_topic: str, sub_info: dict):
        await self.kv_store.create_subscription(
            name=name, realm_topic=realm_topic, sub_info=sub_info
        )

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        await self.kv_store.get_subscriber_info(name=name)

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        await self.kv_store.set_subscriber_queue_status(name=name, sub_info=sub_info)

    async def delete_subscriber_from_key(self, key: str, name: str):
        await self.kv_store.delete_subscriber_from_key(key=key, name=name)

    async def delete_subscriber(self, name: str):
        await self.kv_store.delete_subscriber(name=name)

    async def get_value_by_key(self, key: str):
        await self.kv_store.get_value_by_key(key=key)

    async def put_value_by_key(self, key: str, value: Union[str, dict]):
        await self.kv_store.put_value_by_key(key=key, value=value)

    async def get_subscribers_for_key(self, key: str):
        await self.kv_store.get_subscribers_for_key(key=key)

    async def update_subscribers_for_key(self, key: str, name: str) -> None:
        await self.kv_store.update_subscribers_for_key(key=key, name=name)
