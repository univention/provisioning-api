import contextlib
from typing import Annotated, Coroutine, Iterator

from fastapi import Depends
from nats.aio.client import Client as NATS

from shared.config import settings


async def nats_dependency() -> Coroutine[None, None, Iterator[NATS]]:
    """
    Helper function to inject a NATS connection into FastAPI handlers.
    """
    nc = NATS()
    await nc.connect(servers=[f"nats://{settings.nats_host}:{settings.nats_port}"])
    try:
        yield nc
    finally:
        await nc.close()


NatsDependency = Annotated[NATS, Depends(nats_dependency)]


@contextlib.asynccontextmanager
async def nats_context():
    """
    Obtain a context-managed connection to NATS.
    """
    nc = NATS()
    await nc.connect(servers=[f"nats://{settings.nats_host}:{settings.nats_port}"])
    try:
        yield nc
    finally:
        await nc.close()
