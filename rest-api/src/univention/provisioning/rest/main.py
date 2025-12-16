# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from contextlib import asynccontextmanager

import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_utils.timing import add_timing_middleware

from univention.provisioning.backends.nats_mq import IncomingQueue, PrefillQueue
from univention.provisioning.utils.log import setup_logging

from .config import app_settings
from .message_service import MessageService
from .messages import router as messages_api_router
from .mq_adapter_nats import NatsMessageQueue
from .subscription_service import SubscriptionService
from .subscriptions import router as subscriptions_api_router
from .subscriptions_db_adapter_nats import NatsSubscriptionsDB

logger = logging.getLogger(__name__)


singleton_clients = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Starting up...")
    settings = app_settings()

    # 1. Create and connect the persistent NATS message queue client
    mq = NatsMessageQueue(settings)
    await mq.connect()
    singleton_clients["mq"] = mq

    # 2. Create and connect the persistent Subscriptions DB client
    db = NatsSubscriptionsDB(settings)
    await db.connect()
    singleton_clients["db"] = db

    # 3. Create singleton services
    sub_service = SubscriptionService(subscriptions_db=db, mq=mq)
    singleton_clients["sub_service"] = sub_service
    msg_service = MessageService(subscriptions_db=db, mq=mq)
    singleton_clients["msg_service"] = msg_service

    # 4. Ensure necessary queues exist on startup
    logger.info("Checking MQ connectivity and ensuring queues exist...")
    await mq.create_queue(PrefillQueue())
    await mq.create_queue(IncomingQueue("provisioning-dispatcher"))  # Using a default name

    logger.info("Startup complete. Singleton services are running.")
    yield

    # --- Shutdown ---
    logger.info("Shutting down...")
    await singleton_clients["mq"].close()
    await singleton_clients["db"].close()
    singleton_clients.clear()
    logger.info("Shutdown complete.")


# TODO: Refactor this into functions for better testability
settings = app_settings()
app = FastAPI(
    debug=settings.debug,
    description="APIs for subscription and message handling.",
    root_path=settings.root_path,
    title="Provisioning REST APIs",
    lifespan=lifespan,
)
add_timing_middleware(app, record=logger.info)
app.add_middleware(CorrelationIdMiddleware)

if settings.cors_all:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(subscriptions_api_router)
app.include_router(messages_api_router)


def add_exception_handlers(_app: FastAPI):
    """Workaround for FastAPI not catching exceptions in sub-apps: https://github.com/fastapi/fastapi/issues/1802"""

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> Response:
        """Add Correlation-ID to HTTP 500."""
        return await http_exception_handler(
            request,
            HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Internal server error",
                headers={
                    CorrelationIdMiddleware.header_name: correlation_id.get() or "",
                    "Access-Control-Expose-Headers": CorrelationIdMiddleware.header_name,
                },
            ),
        )


add_exception_handlers(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error("%s: %s", request, exc_str)
    content = {"status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def run():
    settings = app_settings()
    assert settings
    setup_logging(settings.log_level)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7777,
        log_config=None,
    )


if __name__ == "__main__":
    run()
