## Consumer Registration Flow
```mermaid
sequenceDiagram
    actor Consumer
    participant ConsumerRegAPI as Consumer Registration API
    participant ConsumerMgmtAPI as Consumer Management API
    participant NatsQ as Nats Queue
    participant NatsKV as Nats Key Value
    participant PrefillService as Prefill Service
    participant Dispatcher


    Consumer->>ConsumerRegAPI: create new subscription
    activate ConsumerRegAPI
    ConsumerRegAPI->>NatsQ: Create queue(s)
    activate NatsQ
    NatsQ-->>ConsumerRegAPI: ACK
    deactivate NatsQ
    ConsumerRegAPI->>PrefillService: Prefill request
    activate PrefillService
    PrefillService-->>ConsumerRegAPI: ACK
    ConsumerRegAPI->>NatsKV: Save subscription data to KV Store including queue(s) and prefill status:pending
    activate NatsKV
    NatsKV-->>ConsumerRegAPI: ACK
    ConsumerRegAPI-->>Consumer: ACK
    deactivate ConsumerRegAPI
    NatsKV-->>ConsumerMgmtAPI: New Subscription
    activate ConsumerMgmtAPI
    NatsKV-->>Dispatcher: New Subscription
    activate Dispatcher
    deactivate NatsKV
    ConsumerMgmtAPI->>ConsumerMgmtAPI: Activate `empty queue`
    deactivate ConsumerMgmtAPI
    Dispatcher->>Dispatcher: Start dispatching in `final queue`
    PrefillService->>NatsQ: Starts Prefilling `prefill queue`
    Consumer->>ConsumerMgmtAPI: Open Queue Stream
    activate ConsumerMgmtAPI
    ConsumerMgmtAPI-->>Consumer: Stream `empty queue`
    PrefillService->>ConsumerRegAPI: Prefill complete message
    deactivate PrefillService
    activate ConsumerRegAPI
    ConsumerRegAPI->>NatsKV: Updates subscription object
    activate NatsKV
    NatsKV-->>ConsumerRegAPI: ACK
    deactivate ConsumerRegAPI
    NatsKV-->>ConsumerMgmtAPI: Subscription status change
    deactivate NatsKV
    ConsumerMgmtAPI->>ConsumerMgmtAPI: Switch to Prefill queue
    ConsumerMgmtAPI-->>Consumer: Stream prefill events
    ConsumerMgmtAPI->>ConsumerMgmtAPI: Prefill empty
    ConsumerMgmtAPI-->>Consumer: Stream live events
    deactivate Dispatcher
    deactivate ConsumerMgmtAPI
```

## Prefill Flow
```mermaid
sequenceDiagram
    participant ConsumerRegAPI as Consumer Registration API
    participant PrefillService as Prefill Service
    participant NatsQ as Nats Queue
    participant PrefillWorker as Prefill Worker

    PrefillWorker->>NatsQ: Subscribe to events
    ConsumerRegAPI->>PrefillService: Prefill request
    activate PrefillService
    PrefillService->>NatsQ: create worker task
    activate NatsQ
    NatsQ-->>PrefillService: ACK
    NatsQ->>PrefillWorker: New Task
    activate PrefillWorker
    deactivate NatsQ
    PrefillWorker->>PrefillWorker: Do the actual Prefill
    PrefillService->>NatsQ: Watch queue status
    activate NatsQ
    PrefillWorker->>NatsQ: Acknowledge Task
    deactivate PrefillWorker
    NatsQ-->>PrefillService: Queue message acknowledged
    PrefillService-->>ConsumerRegAPI: ACK
    PrefillService->>ConsumerRegAPI: Prefill complete message
    deactivate NatsQ
    deactivate PrefillService
```

## Simplified Prefill Flow

The PrefillService ist just proxying requests. Yes it encapsulates the Prefill process but we distribute the Registration Orchestration across separate components.

In this simplified version
all Provisioning Orchestration is consolidated into one service.
This makes it easier to develop and debug.
The functionality can still be encapsulated into it's own module including Ports and Adapters.

```mermaid
sequenceDiagram
    participant ConsumerRegAPI as Consumer Registration API
    participant NatsQ as Nats Queue
    participant PrefillWorker as Prefill Worker

    PrefillWorker->>NatsQ: Subscribe to events
    activate ConsumerRegAPI
    ConsumerRegAPI->>NatsQ: create worker task
    activate NatsQ
    NatsQ-->>ConsumerRegAPI: ACK
    NatsQ->>PrefillWorker: New Task
    activate PrefillWorker
    deactivate NatsQ
    PrefillWorker->>PrefillWorker: Do the actual Prefill
    ConsumerRegAPI->>NatsQ: Watch queue status
    activate NatsQ
    PrefillWorker->>NatsQ: Acknowledge Task
    deactivate PrefillWorker
    NatsQ-->>ConsumerRegAPI: Queue message acknowledged
    deactivate NatsQ
    deactivate ConsumerRegAPI
```


## Prefill Flow Utilizing Kubernetes Jobs

### TLDR

We can use the operator pattern to accomplish prefill tasks as long as we don't use CRD's (which we don't need anyway)

### Intro

The kubernetes operator pattern:
an `operator` pod manages other kubernetes resources by interacting with the kubernetes api for inside the cluster.

Operators frequently need two things:
- RoleBinding to have read and write access to specific kubernetes object types.
- Custom Resource Definition (CRD) extend the kubernetes api with custom Objects.
These are frequently used to define the desired state that the operator should configure (Give me a 5 node Postgres cluster)

Our understanding was, that this is not allowed in the `openDesk` context.
Thorsten Rossner and Dominik Kaminski clarified this misconception:

The main `openDesk` requirement is: "everything needs to be installable in namespaces"
- RoleBindings are namespace-specific (ClusterRoleBindings are the same but with cluster-scope)
- CRD's are always cluster-scoped **and thus forbidden in the openDesk context**

### Advantages

- Prefill containers are only running when needed
- Kubernetes takes care of retries, exponential backoff...
- What's happening is transparent to the user (Via the kubernetes API)
- Each prefill job gets it's own container
- There are no long-running HTTP API or Daemon processes associated with Prefill.
Instead most of the complexity is moved to the Kubernetes API
and a bit is moved to the Consumer Registration API
- Job status is persisted in the Kubernetes API. All components can crash to their heart's content.
- Once we have implemented the operator pattern, we can extend it to:
    - Scaling up UDM and LDAP containers in preparation for a prefill event
    - Kubernetes Objects defining consumers instead of http request to Consumer Registration API (CRD)

```mermaid
sequenceDiagram
    participant ConsumerRegAPI as Consumer Registration API
    participant KubernetesAPI as Kubernetes API
    participant PrefillWorker as Prefill Worker Job

    activate ConsumerRegAPI
    ConsumerRegAPI->>KubernetesAPI: Create worker ConfigMap
    activate KubernetesAPI
    ConsumerRegAPI->>KubernetesAPI: Create worker Job
    KubernetesAPI-->ConsumerRegAPI: ACK
    KubernetesAPI->>PrefillWorker: Create job and mount ConfigMap
    deactivate KubernetesAPI
    activate PrefillWorker
    ConsumerRegAPI->>KubernetesAPI: Watch Job status
    activate KubernetesAPI
    PrefillWorker->>PrefillWorker: Do the actual Prefill
    PrefillWorker->>KubernetesAPI: Job Completed
    deactivate PrefillWorker
    KubernetesAPI-->>ConsumerRegAPI: Job Complete
    deactivate KubernetesAPI
    deactivate ConsumerRegAPI
```