import os

if os.getenv("READ_CONFIG_FROM_ENVIRONMENT_VARIABLES", "false").lower() == "true":
    from .config_env import LdapProducerSettings, ldap_producer_settings
else:
    from .config_ucr import LdapProducerSettings, ldap_producer_settings

LdapProducerSettings = LdapProducerSettings
ldap_producer_settings = ldap_producer_settings
