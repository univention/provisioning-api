# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache

from pydantic import BaseSettings
from typing import Any, Callable, Dict, Tuple

SettingsSourceCallable = Callable[["BaseSettings"], Dict[str, Any]]


def ucr_nats_mq_settings(settings: BaseSettings) -> Dict[str, Any]:
    try:
        from univention.config_registry import ConfigRegistry
    except ImportError:
        return {}
    ucr = ConfigRegistry()
    ucr.load()

    conf = {
        "num_replicas": ucr.get("nats/num_replicas", 1),
    }
    return conf


class NATSMQSettings(BaseSettings):
    """
    Settings for the NATS message queue.
    """

    num_replicas: int = 1

    class Config:
        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                ucr_nats_mq_settings,
                file_secret_settings,
                env_settings,
            )


@lru_cache(maxsize=1)
def nats_mq_settings() -> NATSMQSettings:
    return NATSMQSettings()