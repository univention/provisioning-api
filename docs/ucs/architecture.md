# Overview

The provisioning service on UCS systems consists of two apps:

- `provisioning-service-backend`: This app installs a listener module that captures LDAP changes
   and writes them to the LDAP-queue. This app is only installed on the Primary Directory Node.
- `provisioning-service`: This app contains the main provisioning service components:
   udm-transformer, prefill, dispatcher, and provisioning API and is installed on the Primary and
   on all Backups.

## Architecture diagram

The following diagram illustrates the data flow in the architecture of the Provisioning Service on UCS systems with
Primary and Backup nodes.

Note that LDAP/UDM changes originate always and only from the Primary's LDAP server.
But other (non-UDM) events can be created anywhere and can be enqueued using any *Provisioning API* instance.
Those events may have to be distributed to other UCS nodes.
Thus, the *Provisioning API* instances on Backup nodes connect to two NATS instances:

- The NATS on their node for the queues of "their" Consumers.
- The NATS on the Primary for enqueuing the non-UDM events they received.

This way the non-UDM events can be pulled by the *Dispatchers* of all nodes.

```mermaid
flowchart LR
    RegularConsumer["Regular
        Consumer 'P'"]
    B1_RegularConsumer["Regular
        Consumer 'B1'"]
    subgraph Primary["Primary"]
        LDAP[(LDAP)]
        subgraph provisioning-service-backend["App provisioning-service-backend"]
            Listener[Listener module]
        end
        LDAPQueue[(LDAP-queue)]


        subgraph provisioning-service["App provisioning-service"]
            Transformer[UDM-Transformer]
            InQueue[("Incoming
            queue")]
            Prefill[Prefill]
            Dispatcher[Dispatcher]
            RegularConsumerQueue[("Regular
            Consumer
            queue 'P'")]
            ProvisioningAPI["Provisioning
            API"]
            NonUDM["Non-UDM
            event source"]

            Listener --> LDAPQueue
            NonUDM --> |Non-UDM event| ProvisioningAPI
            LDAPQueue --> |LDAP event| Transformer --> |UDM event| ProvisioningAPI --> |All events| InQueue
            InQueue --> |Events for Primary's consumers, e.g. 'P'| Dispatcher
            Dispatcher --> |P's events| RegularConsumerQueue
            Prefill --> |P's events| RegularConsumerQueue
            RegularConsumerQueue --> |P's events| ProvisioningAPI 
        end

        LDAP --> Listener
    end

    subgraph Backup1["Backup1"]

        subgraph B1_provisioning-service["App provisioning-service"]
            B1_Dispatcher[ Dispatcher]
            B1_Prefill[Prefill]
            B1_RegularConsumerQueue[("Regular
            Consumer
            queue 'B1'")]
            B1_ProvisioningAPI["Provisioning
            API"]
            B1_NonUDM["Non-UDM
            event source"]


            B1_Dispatcher --> |B1's events| B1_RegularConsumerQueue
            B1_Prefill --> |B1's events| B1_RegularConsumerQueue
            B1_NonUDM --> |Non-UDM event| B1_ProvisioningAPI
            B1_RegularConsumerQueue --> |B1's events| B1_ProvisioningAPI
            B1_ProvisioningAPI --> |Non-UDM event| InQueue
        end
    end

    InQueue --> |Events for Backup1's consumers, e.g. 'B1'| B1_Dispatcher
    InQueue
    B1_Prefill
    ProvisioningAPI --> |P's events| RegularConsumer
    B1_ProvisioningAPI --> |B1's events| B1_RegularConsumer
```

Alternative drawing:

![Provisioning on UCS](Provisioning_on_UCS.png "Provisioning on UCS")

## Differences to N4K Provisioning Service

There are a few differences between the implementation on UCS and N4K:

- On UCS, the dispatcher of each backup needs to read from the incoming queue of the primary. In
  N4K, there is just one instance of the dispatcher and backups don't exist.
- Due to that difference, on UCS, the incoming queue is required to use the retention
  policy `INTEREST` to allow multiple consumers getting the same messages.
  In N4K, the incoming queue uses the default retention policy `WORKQUEUE` as there is only one
  consumer (the dispatcher).
