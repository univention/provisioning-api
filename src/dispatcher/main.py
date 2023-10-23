#!/usr/bin/env python3

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from .api import router as api_router
from core.log import setup as setup_logging


setup_logging()

openapi_tags = [
    {
        "name": "admin",
        "description": "Administrative actions",
    },
    {
        "name": "sink",
        "description": "Subscriber to LDAP changes",
    },
    {
        "name": "source",
        "description": "Source of LDAP changes",
    },
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

app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
