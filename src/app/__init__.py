# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uvicorn


def start_dev():
    """
    Helper function for running with `poetry run dev`.
    """
    uvicorn.run(
        "app.main:app",
        log_config="logging.yaml",
        host="0.0.0.0",
        port=7777,
        reload=True,
    )
