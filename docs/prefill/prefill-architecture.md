## Consumer Registration Flow

### Without Prefill
```mermaid
sequenceDiagram
    actor Consumer
    participant ConsumerRegAPI as Consumer Registration API
    participant ConsumerMessagesAPI as Consumer Messages API
    participant NatsQ as Nats Queue
    participant NatsKV as Nats Key Value
    participant Dispatcher


    Consumer->>ConsumerRegAPI: create new subscription
    activate ConsumerRegAPI
    Note over ConsumerRegAPI: see *1
    ConsumerRegAPI->>NatsQ: Create queue
    activate NatsQ
    NatsQ-->>ConsumerRegAPI: ACK
    deactivate NatsQ
    ConsumerRegAPI->>NatsKV: Save subscription data to KV Store including queue(s) and prefill status:pending
    activate NatsKV
    NatsKV-->>ConsumerRegAPI: ACK
    ConsumerRegAPI-->>Consumer: ACK
    deactivate ConsumerRegAPI
    Note over NatsKV: see *1
    Consumer->>ConsumerMessagesAPI: Open Queue Stream
    activate ConsumerMessagesAPI
    ConsumerMessagesAPI->>NatsKV: Get Consumer Object from DB
    NatsKV-->ConsumerMessagesAPI: Return Consumer Object from DB
    ConsumerMessagesAPI->>NatsQ: Subscribe to events
    NatsQ-->>ConsumerMessagesAPI: Stream queue events
    ConsumerMessagesAPI-->>Consumer: Stream live events
    NatsKV-->>Dispatcher: New Subscription
    activate Dispatcher
    deactivate NatsKV
    Dispatcher-->>NatsQ: Start dispatching in `final queue`
    deactivate Dispatcher
    deactivate ConsumerMessagesAPI
```

### With Prefill
```mermaid
sequenceDiagram
    actor Consumer
    participant ConsumerRegAPI as Consumer Registration API
    participant ConsumerMessagesAPI as Consumer Messages API
    participant NatsQ as Nats Queue
    participant NatsKV as Nats Key Value
    participant PrefillService as Prefill Service
    participant Dispatcher


    Consumer->>ConsumerRegAPI: create new subscription
    activate ConsumerRegAPI
    Note over ConsumerRegAPI: see *1
    ConsumerRegAPI->>NatsQ: Create queue(s)
    activate NatsQ
    NatsQ-->>ConsumerRegAPI: ACK
    deactivate NatsQ
    ConsumerRegAPI->>PrefillService: Prefill request
    activate PrefillService
    PrefillService-->>ConsumerRegAPI: ACK
    Note over PrefillService: The Prefill flow<br/>is described<br/> in a separate diagram
    ConsumerRegAPI->>NatsKV: Save subscription data to KV Store including queue(s) and prefill status:pending
    activate NatsKV
    NatsKV-->>ConsumerRegAPI: ACK
    ConsumerRegAPI-->>Consumer: ACK
    deactivate ConsumerRegAPI
    Note over NatsKV: see *1
    Consumer->>ConsumerMessagesAPI: Open Queue Stream
    activate ConsumerMessagesAPI
    ConsumerMessagesAPI->>NatsKV: Get Consumer Object from DB
    NatsKV-->ConsumerMessagesAPI: Return Consumer Object from DB
    Note over ConsumerMessagesAPI: see *2
    ConsumerMessagesAPI-->>Consumer: Stream `empty queue`
    ConsumerMessagesAPI->>NatsKV: Watch Consumer Object Changes
    NatsKV-->>Dispatcher: New Subscription
    activate Dispatcher
    Dispatcher->>Dispatcher: Start dispatching in `final queue`
    PrefillService->>NatsQ: Starts Prefilling `prefill queue`
    PrefillService->>ConsumerRegAPI: Prefill complete message
    deactivate PrefillService
    activate ConsumerRegAPI
    ConsumerRegAPI->>NatsKV: Updates subscription object
    NatsKV-->>ConsumerRegAPI: ACK
    deactivate ConsumerRegAPI
    NatsKV-->>ConsumerMessagesAPI: Subscription prefill status:done
    deactivate NatsKV
    ConsumerMessagesAPI->>NatsQ: Subscribe to events
    NatsQ-->>ConsumerMessagesAPI: Stream queue events
    ConsumerMessagesAPI->>ConsumerMessagesAPI: Switch to Prefill queue
    ConsumerMessagesAPI-->>Consumer: Stream prefill events
    ConsumerMessagesAPI->>ConsumerMessagesAPI: Prefill empty
    ConsumerMessagesAPI-->>Consumer: Stream live events
    deactivate Dispatcher
    deactivate ConsumerMessagesAPI
```

All necessary data about consumers is persisted in the `Nats` key-value store. The Consumer Registration API has write-access to it while the Consumer Management API has read-access.

*1 No prefill for this example. What happens if a new Consumer is written to the key-value store, but no queues have been created yet. Currently the queue is created when the first message is sent by the dispatcher.
Solutions:
- The create new subscription request is only answered with a 200 OK if the needed queue(s) have been created and object has been persisted into the KV Store.
If any of this failed, the request has to be retried
- The ConsumerManagementAPI needs to retry for a bit and then fail if no queues are there. The Queue might be uninitialized until it's first message, which is an undefined time span.

*2 The Prefill queue needs to be blocked. It should appear to the consumer as if the queue is empty. No matter how the queues are managed in the background.

## Simplified Prefill Flow

We decided to implement the "Simplified Prefill" as a first step.

It's advantages are:
- Simpler to develop
- Simpler to debug
- Less risky compared to the Kubernetes Operator solution.
-


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
    PrefillWorker->>NatsQ: In progress acknowledgement
    PrefillWorker->>ConsumerRegAPI: Queue message acknowledged
    PrefillWorker->>NatsQ: Final acknowledgement
    deactivate PrefillWorker
    deactivate ConsumerRegAPI
```

`create worker task` means that the Consumer Registration API creates a new task message in a dedicated Prefill Worker queue.
This persists the prefill request and enables automatic retries.

## Prefill Flow Utilizing Kubernetes Jobs

### TLDR

We can use the operator pattern to accomplish prefill tasks as long as we don't use CRD's (which we don't need anyway)

### Intro

The Kubernetes operator pattern:
an `operator` pod manages other Kubernetes resources by interacting with the Kubernetes API for inside the cluster.

Operators frequently need two things:
- RoleBinding to have read and write access to specific Kubernetes object types.
- Custom Resource Definition (CRD) extend the Kubernetes API with custom Objects.
These are frequently used to define the desired state that the operator should configure (Give me a 5 node PostgreSQL cluster)

Our understanding was, that this is not allowed in the `openDesk` context.
`Thorsten Rossner` and `Dominik Kaminski` clarified this misconception:

The main `openDesk` requirement is: "everything needs to be installed in one namespace"
- RoleBindings are namespace-specific (ClusterRoleBindings are the same but with cluster-scope)
- CRD's are always cluster-scoped **and thus forbidden in the openDesk context**

### Advantages

- Prefill containers are only running when needed
- Kubernetes takes care of retries, exponential back-off...
- What's happening is transparent to the user (Via the Kubernetes API)
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
