Target directory structure:

/src
    /core
    /consumer
        /messages
            /service (dispatcher)
            /api
        /subscriptions
            /api
    /producer
        /service
        /api
    /mom
        (/service would be MQ-framework)
        /api
    /prefill
        /service
        /api


Open points:
- Verification of rights and credentials on every message could be overkill.
    If it is only about Ox accessing users/user, this will never change and can be checked at subscription time.
- What is the difference between Authn/z and Credentials store?
    - Which Authentication layer?
- How much do we need to stick to the architectural design in the presentation?
- Is the split between consumer.messages and consumer.subscriptions really necessary? (i.e. Consumer REST API/Consumer Registration API)