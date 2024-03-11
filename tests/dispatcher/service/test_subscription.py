# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from prefill.service.udm_prefill import match_topic


def test_subscription_match():
    test_cases = [
        # list of test cases:
        # subscription sub.topic, target.topic, expected result
        ("users/user", "users/user", True),
        ("users/user", "groups/group", False),
        ("users/.*", "users/user", True),
        ("users/.*", "groups/group", False),
        (".*", "users/user", True),
        (".*", "groups/group", True),
    ]

    for sub_topic, target_topic, expectation in test_cases:
        assert match_topic(sub_topic, target_topic) == expectation
