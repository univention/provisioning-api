from typing import Annotated, Iterator

from fastapi import Depends
import redis.asyncio as redis

from dispatcher.config import settings


async def get_redis() -> Iterator[redis.Redis]:
    """Obtain a connection to Redis."""
    try:
        connection = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
            protocol=3,
        )
        yield connection
    finally:
        await connection.close()


# Define the type for FastAPI dependency injection here.
# Defining it once allows more easily replacing the implementation in the future.
RedisDependency = Annotated[redis.Redis, Depends(get_redis)]
