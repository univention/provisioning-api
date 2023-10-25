## Design

The implementation follows this [design document](https://git.knut.univention.de/univention/internal/swp-infocenter/-/tree/main/topics/provisioning)


## Target directory structure

```
/src
    /core
    /consumer
        /messages
            /service (dispatcher)
            /api
        /subscriptions
            /api
    /mom
        (/service would be MQ-framework)
        /api
    /dispatcher
        /service
    /producer
        /service
        /api
    /prefill
        /service
        /api
```


## Current status of refactoring

Dispatcher PoC has been split up into 2 services

- **Consumer**
  - **Messages** (Represents _Consumer REST API_ and might need renaming on either side)
  - **Subscriptions** (Represents _Consumer Registration REST API_ and might need renaming on either side)


Prefill, Producer, MOM are prepared and will be implemented as we go.

## Assumptions and Thoughts

### Components' Responsibilities

#### _Producer Service_ / _Notification REST API_

The reason for _Notification API clients_ not directly communicating to the _MOM REST API_ is, that other types of notifications than UDM are possible (e.g. security related) and therefore, an additional abstraction layer is provided.

This could also be possible within the _MOM REST API_. A similar structure as in the _Consumer Worker_ can be imagined, having the split on code level rather than on process level.

#### _Dispatcher Service_

This might become a service on the level of a seperate python module as part of the _MOM Service_.

#### _Consumer Worker_

This is currently realized as one FastAPI app with two routers. It can be split later if independent scaling is required.

## Open points and questions

Answers from Daniel Tröder (out of meeting on MVP 2023-10-25):

Q: What is the difference between Authn/z and Credentials store? Which Authentication layer? \
A: Credentials Store is between REST APIs and MOM, Authn/z is for clients of REST APIs.

Q: How much do we need to stick to the architectural design in the presentation? \
A: It is advised to stick to the design and requested to update the design or document wherever a deviation is deemed necessary.

Q: Is the split between consumer.messages and consumer.subscriptions really necessary? (i.e. Consumer REST API/Consumer Registration API) \
A: They are used by different clients (i.e. Apps and Operators), so, yes

- Verification of rights and credentials on every message could be overkill.
  If it is only about Ox accessing users/user, this will never change and can be checked at subscription time.