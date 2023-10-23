import contextlib
from typing import Annotated, Coroutine, Iterator

from fastapi import Depends
import redis.asyncio as redis

from core.config import settings


async def redis_dependency() -> Coroutine[None, None, Iterator[redis.Redis]]:
    """
    Helper function to inject a Redis connection into FastAPI handlers.

    This function should not be called directly but used through the
    `RedisDependency`.
    """
    connection = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        protocol=3,
    )
    try:
        yield connection
    finally:
        await connection.close()


# The actual type for FastAPI dependency injection here.
RedisDependency = Annotated[redis.Redis, Depends(redis_dependency)]


@contextlib.asynccontextmanager
async def redis_context():
    """
    Obtain a context-managed connection to Redis.

    Usage:
    ```
    async with redis_context() as redis:
        redis.ping()
    ```
    """
    connection = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        protocol=3,
    )
    try:
        yield connection
    finally:
        await connection.close()
