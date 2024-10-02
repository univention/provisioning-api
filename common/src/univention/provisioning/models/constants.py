# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from enum import Enum

LDIF_STREAM = "ldif-producer"
LDAP_STREAM = "ldap-producer"
PREFILL_STREAM = "prefill"
DISPATCHER_SUBJECT_TEMPLATE = "{subscription}.main"
DISPATCHER_STREAM = "incoming"
PREFILL_SUBJECT_TEMPLATE = "{subscription}.prefill"


class Bucket(str, Enum):
    subscriptions = "SUBSCRIPTIONS"
    credentials = "CREDENTIALS"
    cache = "CACHE"


class PublisherName(str, Enum):
    udm_listener = "udm-listener"
    ldif_producer = "ldif-producer"
    udm_pre_fill = "udm-pre-fill"
    consumer_registration = "consumer-registration"
    consumer_client_test = "consumer_client_test"
