# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc
from typing import Optional


class PreFillService(abc.ABC):
    MAX_PREFILL_ATTEMPTS = 3

    def __init__(self):
        self._topic: Optional[str] = None
