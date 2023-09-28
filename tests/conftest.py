import pytest
from fakeredis import aioredis
from dispatcher.main import app
from dispatcher.persistence.redis import redis_dependency


async def redis_fake_dependency():
    connection = aioredis.FakeRedis(decode_responses=True, protocol=3)
    try:
        yield connection
    finally:
        await connection.close()


@pytest.fixture(scope="session", autouse=True)
def override_dependencies():
    # Override original redis
    app.dependency_overrides[redis_dependency] = redis_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
