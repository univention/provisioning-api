

```mermaid
%% Example of sequence diagram
  sequenceDiagram
    ConsumerApp->>ConsumerAPI: subscribe (realm:udm, topic:users/user, consumer:OX)
    ConsumerAPI->>ConsumerRegistrationAPI: subscribe (realm:udm, topic:users/user, consumer:OX)
    ConsumerRegistrationAPI->>MOM: create consumer queue
    MOM->>ConsumerAPI: stream message
    ConsumerAPI->>ConsumerApp: stream message
```
