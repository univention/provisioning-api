import pytest

"""
- LDAP Change is triggered via UDM REST API
- LDAP Notifier will notify its listeners
    - how are listeners registered with notifier?
- UDM listener is called and will
    - update the old cache for references
    - enrich the LDAP object by resolving references
        - using UDM REST API (new ref) or old cache (old ref)
    - send the full UDM object to the event API
- Event API will store in incoming queue
- Dispatcher will dispatch
- Consumer will receive message
"""


@pytest.mark.xfail()
def test_udm_event_is_routed_properly():
    raise NotImplementedError
