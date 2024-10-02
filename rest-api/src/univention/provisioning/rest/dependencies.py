# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import AppSettings, app_settings

http_basic = HTTPBasic()

AppSettingsDep = Annotated[AppSettings, Depends(app_settings)]
HttpBasicDep = Annotated[HTTPBasicCredentials, Depends(http_basic)]


def authenticate_user(credentials: HTTPBasicCredentials, username: str, password: str) -> None:
    is_correct_username = secrets.compare_digest(credentials.username.encode("utf8"), username.encode("utf8"))
    is_correct_password = secrets.compare_digest(credentials.password.encode("utf8"), password.encode("utf8"))
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def authenticate_admin(credentials: HttpBasicDep, settings: AppSettingsDep) -> None:
    authenticate_user(credentials, settings.admin_username, settings.admin_password)


def authenticate_events_endpoint(credentials: HttpBasicDep, settings: AppSettingsDep) -> None:
    authenticate_user(
        credentials,
        settings.events_username_udm,
        settings.events_password_udm,
    )


def authenticate_prefill(credentials: HttpBasicDep, settings: AppSettingsDep) -> None:
    authenticate_user(credentials, settings.prefill_username, settings.prefill_password)
