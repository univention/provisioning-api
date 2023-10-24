import consumer.messages.service.subscription


def test_subscription_match():
    test_cases = [
        # list of test cases:
        # subscription realm, sub. topic, message realm, msg. topic, expected result
        ("udm", "users/user", "udm", "users/user", True),
        ("udm", "users/user", "udm", "groups/group", False),
        ("udm", "users/user", "mdu", "users/user", False),
        ("udm", "users/.*", "udm", "users/user", True),
        ("udm", "users/.*", "udm", "groups/group", False),
        ("udm", ".*", "udm", "users/user", True),
        ("udm", ".*", "udm", "groups/group", True),
    ]

    for sub_realm, sub_topic, msg_realm, msg_topic, expectation in test_cases:
        assert (
            consumer.messages.service.subscription.match_subscription(
                sub_realm, sub_topic, msg_realm, msg_topic
            )
            == expectation
        )
