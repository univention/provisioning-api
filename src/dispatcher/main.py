import asyncio

from src.dispatcher.port import DispatcherPort
from src.dispatcher.service.dispatcher import DispatcherService


async def main():
    async with DispatcherPort.port_context() as port:
        service = DispatcherService(port)
        await service.store_event_in_consumer_queues()


if __name__ == "__main__":
    asyncio.run(main())
