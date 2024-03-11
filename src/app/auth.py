# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import secrets

from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials


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
