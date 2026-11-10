# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
Register every subscription spec in a directory at the Provisioning API.

This is the main process of the register-consumers Job.
Every `*.json` file is one subscription spec, whose `password` is a string
or a `kubernetes_secret` reference.
Every spec is tried; the exit code is 1 if one of them failed.
"""

import asyncio
import enum
import json
import logging
import sys
from pathlib import Path
from typing import Awaitable, Callable, Literal, TypeVar

import aiohttp
from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings

from univention.provisioning.models.subscription import NewSubscription

from .admin import AdminClient, ProvisioningApiError, SubscriptionConflict, SubscriptionCreation
from .kubernetes_secrets import (
    InvalidReference,
    KubernetesSecretReader,
    SecretReadError,
    SecretReference,
    is_reference,
    parse_reference,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RegisterConsumersSettings(BaseSettings):
    provisioning_api_base_url: str
    admin_username: str
    admin_password: SecretStr
    specs_dir: Path = Path("/secrets")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    # Short on purpose: Kubernetes reruns a failed Job, so only blips are worth waiting for here.
    retry_attempts: int = Field(default=3, ge=1)
    retry_delay: float = Field(default=1.0, ge=0)


class SpecError(ValueError):
    pass


class Outcome(enum.Enum):
    CREATED = "created"
    UNCHANGED = "unchanged"
    FAILED = "failed"


ReaderFactory = Callable[[], KubernetesSecretReader]


class LazyReader:
    """Builds the Kubernetes reader on the first reference, so specs with string passwords need no cluster."""

    def __init__(self, factory: ReaderFactory):
        self.factory = factory
        self.reader: KubernetesSecretReader | None = None

    async def get(self, reference: SecretReference) -> str:
        if self.reader is None:
            self.reader = self.factory()
        return await self.reader.get(reference)

    async def close(self):
        if self.reader is not None:
            await self.reader.close()


def is_transient(error: BaseException) -> bool:
    if isinstance(error, ProvisioningApiError):
        return error.status >= 500
    if isinstance(error, SecretReadError):
        return error.transient
    return isinstance(error, (aiohttp.ClientError, asyncio.TimeoutError))


async def with_retries(operation: Callable[[], Awaitable[T]], what: str, attempts: int, delay: float) -> T:
    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except Exception as error:
            if attempt == attempts or not is_transient(error):
                raise
            logger.warning(
                "%s: attempt %d of %d failed: %s; retrying in %gs",
                what,
                attempt,
                attempts,
                describe(error),
                delay,
            )
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")


def describe(error: BaseException) -> str:
    return str(error) or type(error).__name__


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError) as error:
        raise SpecError(f"cannot read the spec: {error}") from None
    except json.JSONDecodeError as error:
        raise SpecError(f"the spec is not valid JSON: {error.msg} at line {error.lineno}") from None
    if not isinstance(spec, dict):
        raise SpecError("the spec must be a JSON object")
    return spec


def build_subscription(spec: dict, password: str) -> NewSubscription:
    try:
        return NewSubscription.model_validate({**spec, "password": password})
    except ValidationError as error:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in problem['loc'])}: {problem['msg']}"
            for problem in error.errors(include_input=False, include_url=False)
        )
        raise SpecError(f"invalid spec: {problems}") from None


async def resolve_password(spec: dict, secrets: LazyReader, settings: RegisterConsumersSettings):
    """Returns the password and, if it came from a Secret, the reference."""
    value = spec.get("password")
    if isinstance(value, str):
        return value, None
    if not is_reference(value):
        raise SpecError("password must be a string or a {'kubernetes_secret': {'name', 'key'}} reference")
    try:
        reference = parse_reference(value)
    except InvalidReference as error:
        raise SpecError(f"invalid password reference: {error}") from None
    password = await with_retries(
        lambda: secrets.get(reference), f"Reading {reference}", settings.retry_attempts, settings.retry_delay
    )
    return password, reference


async def register_spec(
    path: Path,
    client: AdminClient,
    secrets: LazyReader,
    settings: RegisterConsumersSettings,
) -> Outcome:
    consumer = path.stem
    try:
        spec = load_spec(path)
        password, reference = await resolve_password(spec, secrets, settings)
        subscription = build_subscription(spec, password)
    except (SpecError, SecretReadError) as error:
        logger.error("Failed to register the consumer %s: %s", consumer, describe(error))
        return Outcome.FAILED

    logger.info(
        "Registering the consumer %s: subscription %r, %d realm-topic pairs, request_prefill=%s, password from %s",
        consumer,
        subscription.name,
        len(subscription.realms_topics),
        subscription.request_prefill,
        reference or "the spec",
    )
    try:
        result = await with_retries(
            lambda: client.create_subscription(subscription),
            f"Registering the consumer {consumer}",
            settings.retry_attempts,
            settings.retry_delay,
        )
    except SubscriptionConflict as error:
        logger.error(
            "Failed to register the consumer %s: HTTP %d. The subscription %r already exists "
            "with a different password or config. Changing either is not supported, "
            "because deleting the subscription drops its queue. Response: %s",
            consumer,
            error.status,
            subscription.name,
            error.body,
        )
        return Outcome.FAILED
    except ProvisioningApiError as error:
        logger.error("Failed to register the consumer %s: HTTP %d. Response: %s", consumer, error.status, error.body)
        return Outcome.FAILED
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        logger.error("Failed to register the consumer %s: Provisioning API unreachable: %s", consumer, describe(error))
        return Outcome.FAILED

    if result is SubscriptionCreation.CREATED:
        logger.info("Registered the consumer %s", consumer)
        return Outcome.CREATED
    logger.info("The consumer %s is already registered with the same parameters", consumer)
    return Outcome.UNCHANGED


async def register_all(
    settings: RegisterConsumersSettings,
    reader_factory: ReaderFactory = KubernetesSecretReader.from_service_account,
) -> int:
    paths = sorted(settings.specs_dir.glob("*.json"))
    if not paths:
        logger.info("No subscription specs (*.json) in %s, nothing to register", settings.specs_dir)
        return 0

    secrets = LazyReader(reader_factory)
    outcomes = []
    try:
        async with AdminClient(
            settings.provisioning_api_base_url,
            settings.admin_username,
            settings.admin_password.get_secret_value(),
        ) as client:
            for path in paths:
                outcomes.append(await register_spec(path, client, secrets, settings))
    finally:
        await secrets.close()

    logger.info(
        "%d created, %d unchanged, %d failed",
        outcomes.count(Outcome.CREATED),
        outcomes.count(Outcome.UNCHANGED),
        outcomes.count(Outcome.FAILED),
    )
    return 1 if Outcome.FAILED in outcomes else 0


def run():
    settings = RegisterConsumersSettings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)-7s %(message)s",
        stream=sys.stdout,
    )
    sys.exit(asyncio.run(register_all(settings)))


if __name__ == "__main__":
    run()
