import logging
from udm_messaging.port import UDMMessagingPort
from udm_messaging.service.udm import UDMMessagingService

__package__ = ""  # workaround for PEP 366
name = "LDAP-listener"
description = "LDAP-listener"
attribute = []

logging.basicConfig(filename="ldap_listener/logfile.log", level=logging.INFO)

async with UDMMessagingPort.port_context() as port:
    service = UDMMessagingService(port)


def handler(dn, new, old):
    """
    This function is called on each change.
    """
    if new and old:
        _handle_modify(dn, new, old)
    elif new and not old:
        _handle_create(dn, new)
    elif old and not new:
        _handle_remove(dn, old)


def _handle_modify(dn, new, old):
    """
    Called when an object is modified.
    """
    logging.info(f'Edited user "{old}"')
    service.handle_changes()


def _handle_create(dn, new):
    """
    Called when an object is newly created.
    """
    logging.info(f'Added user "{new}"')
    service.handle_changes()


def _handle_remove(dn, old):
    """
    Called when an previously existing object is removed.
    """
    logging.info(f'Removed user "{old}"')
    service.handle_changes()
