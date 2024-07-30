#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from server.config import settings
from server.core.app.admin.api import router as admin_api_router
from server.core.app.consumer.messages.api import router as messages_api_router
from server.core.app.consumer.subscriptions.api import (
    router as subscriptions_api_router,
)
from server.core.app.internal.api import router as internal_api_router
from server.services.port import Port
from univention.provisioning.models.queue import PREFILL_STREAM

# TODO split up logging
# from .log import setup as setup_logging


# setup_logging()

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

internal_app.include_router(admin_api_router)
internal_app.include_router(internal_api_router)
internal_app_path = "/internal"

app.mount(internal_app_path, internal_app)


@app.on_event("startup")
async def startup_task():
    logging.info("ensuring prefill stream")

    async with Port.port_context() as port:
        await port.create_stream(PREFILL_STREAM)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error("%s: %s", request, exc_str)
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
