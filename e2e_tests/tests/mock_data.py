# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.provisioning.consumer.api import RealmTopic

REALM = "udm"
GROUPS_TOPIC = "groups/group"
USERS_TOPIC = "users/user"
DUMMY_TOPIC = "tests/topic"
USERS_REALMS_TOPICS = [RealmTopic(realm=REALM, topic=USERS_TOPIC)]
DUMMY_REALMS_TOPICS = [RealmTopic(realm=REALM, topic=DUMMY_TOPIC)]
