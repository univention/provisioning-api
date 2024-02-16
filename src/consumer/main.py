#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .messages.api import router as messages_api_router
from .subscriptions.api import router as subscriptions_api_router
from admin.api import router as admin_api_router
from internal.api import router as internal_api_router
from shared.config import settings

# TODO split up logging
# from .log import setup as setup_logging


# setup_logging()

openapi_tags = [
    {
        "name": "sink",
        "description": "Subscriber to LDAP changes",
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
app.include_router(admin_api_router)
app.include_router(internal_api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error("%s: %s", request, exc_str)
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
