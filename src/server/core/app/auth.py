# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import secrets
from typing import Annotated
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from src.server.core.app.config import app_settings

security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials, username: str, password: str):
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), password.encode("utf8")
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def authenticate_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    authenticate_user(
        credentials, app_settings.admin_username, app_settings.admin_password
    )
