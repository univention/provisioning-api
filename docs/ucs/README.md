# Provisioning Service Documentation for UCS Systems

## Overview

The *Nubus Provisioning* service was originally designed for running in Kubernetes.
It was then migrated to UCS.
UCS' system role concept (Primary, Backup, Replica, Memberserver) requires the Provisioning system
to work slightly different in UCS and Kubernetes,
with the main differences being in the "NATS cluster management" (see section *Architecture*)
and the *Backup to Primary failover* mechanism (see section of the same name).

## Architecture

The provisioning service on UCS systems consists of two apps:

- `provisioning-service-backend`: This app installs a listener module that captures LDAP changes
   and writes them to the LDAP-queue. This app is only installed on the Primary Directory Node.
- `provisioning-service`: This app contains the main provisioning service components:
   udm-transformer, prefill, dispatcher, and provisioning API and is installed on the Primary and
   on all Backups.

See [architecture.md](architecture.md) for an in-depth explanation of the architecture of the
provisioning service on UCS.

## Backup to Primary failover (univention-backup2master)

The provisioning service supports backup to primary failover.

The backup-to-primary scenario is automatically handled via
`apps/50provisioning-service-backup2master`, which is executed during `univention-backup2master`.
It installs the `provisioning-service-backend` app on the new Primary Directory Node and
reinitializes the `provisioning-service` app.

Location of the script on a UCS system:

> /usr/lib/univention-backup2master/post/50provisioning-service-backup2master

### Manual steps after univention-backup2master

- On all remaining Backup Directoy Nodes:
  - follow this article (specifically `ldap/master` needs to be correct):
    https://help.univention.com/t/how-to-backup2master/19514
  -execute `univention-app configure provisioning-service --set provisioning-service/udm-rest-api-host=<REPLACE_ME> --set provisioning-service/primary/url=<REPLACE_ME>"`
- Restart all provisioning consumers (they usually just terminate and in k8s that's enough to
  trigger the automatic restart, but not in UCS).

## Automatic Tests

- [5.2-3 provisioning Product Tests](https://jenkins2022.knut.univention.de/job/UCS-5.2/job/UCS-5.2-3/view/Product%20Tests/job/product-test-base-provisioning/)
