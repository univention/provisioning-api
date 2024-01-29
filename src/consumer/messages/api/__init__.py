# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from fastapi import APIRouter

from .v1 import router as router_v1

name = "/messages"
v1_prefix = f"{name}/v1"

router = APIRouter()
router.include_router(router_v1, prefix=v1_prefix)
