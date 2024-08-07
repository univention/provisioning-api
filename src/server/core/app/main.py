#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import logging
from importlib.metadata import version

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_utils.timing import add_timing_middleware

from server.config import settings
from server.core.app.admin.api import router as admin_api_router
from server.core.app.consumer.messages.api import router as messages_api_router
from server.core.app.consumer.subscriptions.api import (
    router as subscriptions_api_router,
)
from server.core.app.internal.api import router as internal_api_router
from server.log import setup_logging
from server.services.port import Port
from univention.provisioning.models.queue import PREFILL_STREAM

setup_logging()
logger = logging.getLogger(__name__)

openapi_tags = [
    {
        "name": "subscriptions",
        "description": "Subscription management actions",
    }
]

app = FastAPI(
    debug=settings.debug,
    description="Forward LDAP changes to subscribers",
    openapi_tags=openapi_tags,
    root_path=settings.root_path,
    title="Provisioning Dispatcher",
    version="v1",
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

app.include_router(messages_api_router)
app.include_router(subscriptions_api_router)


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

internal_openapi_tags = [
    {
        "name": "admin",
        "description": "Administrative actions",
    },
    {
        "name": "internal",
        "description": "Internal actions",
    },
]
internal_app = FastAPI(
    debug=settings.debug,
    description="Internal endpoints for Provisioning Dispatcher",
    openapi_tags=internal_openapi_tags,
    root_path=settings.root_path,
    title="Internal API",
    version="v1",
)
add_exception_handlers(internal_app)
internal_app.include_router(admin_api_router)
internal_app.include_router(internal_api_router)
internal_app_path = "/internal"

app.mount(internal_app_path, internal_app)


@app.on_event("startup")
async def startup_task():
    logger.info("Started %s version %s.", app.title, version("provisioning"))

    async with Port.port_context() as port:
        logger.info("Checking MQ connectivity...")
        await port.ensure_stream(PREFILL_STREAM, False)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logger.error("%s: %s", request, exc_str)
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
