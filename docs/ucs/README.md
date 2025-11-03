# Provisioning Service Documentation for UCS Systems

## Overview
The provisioning component aims to send information from the leading LDAP directory to 3rd-party services.

## Architecture
The provisioning service on UCS systems consists of two apps:
 - `provisioning-service-backend`: This app install a listener module to capture the LDAP changes and push writes them to LDAP-queue.  
This app is only installed on the primary system.
 - `provisioning-service`: This app contains the main provisioning service components, udm-transformer, prefill, dispatcher, and provisioning API.

See [architecture.md](architecture.md) for an in-depth explanation of the architecture of the provisioning service on UCS systems.

## Backup to Master Failover
The provisioning service supports backup to master failover.
- [TODO: link to the jenkins job that tests backup2master]

## Automate Tests

- [5.2-3 provisioning Product Tests](https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-3/view/Product%20Tests/job/product-test-component-provisioning-primary/)