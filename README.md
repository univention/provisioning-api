# Disclaimer - MVP, work in progress

It contains MVP created in context of the openDesk project.

# Provisioning

Tooling for provisioning LDAP objects to external services.

## Components

- [Dispatcher service](./src/dispatcher/)

  The central service to receive LDAP changes and forward them to subscribed clients.

- [Core and client library](src/shared/)

  Everything needed to implement a client.

- [Example client](./src/example-client/)

  An example implementation of a client.

## Usage Overview

### Start dependencies

Build containers for testing:
```sh
docker compose build
```

Run containers:

```sh
docker compose up --detach --remove-orphans
```

### Create a Subscription
To create a subscription, open http://localhost:7777/docs and find the method called 'Create Subscription'.
Enter the following data into the request body:

```sh
{
  "name": "subscription1",
  "realms_topics": [
    ["udm", "groups/group"]
  ],
  "request_prefill": true
}
```

### Trigger the LDAP

To make a change in the LDAP, open http://localhost:8001.

Enter with:
  - **Login DN:** cn=admin,dc=univention-organization,dc=intranet
  - **Password:** univention

Find an entry with `univentionObjectType` = 'groups/group' and modify it.

### Get the Messages

To retrieve messages for the subscriber, open http://localhost:7777/docs.
Find the method named 'Get Subscription Messages' and execute it.

Now, you see the messages, that the subscriber received from the udm-pre-fill process and udm-listener

### Installation

Ensure that you have [`poetry`](https://python-poetry.org/docs/) installed.

If desired, set poetry to create a virtualenv in the project directory:
```sh
poetry config virtualenvs.in-project true
```

Install the dependencies:
```sh
poetry install --with dev
```

### Run the example client

```sh
docker compose up example-client
```


## Tests

### Unit or Integration tests

```sh
poetry run pytest <dir/of/test-subset>
```

### E2E tests


#### Using docker compose

First, start the provisioning-components:

```sh
docker compose up --detach --remove-orphans
```

optimized command:

```sh
docker compose up --pull always --build events-and-consumer-api nats dispatcher prefill udm-listener ldap-notifier udm-rest-api ldap-server
```

Wait for up to 1 minute for the default LDAP changes to be processed by the dispatcher.

Then run the e2e tests.

```sh
poetry run pytest tests/e2e/
```

optimized command:

```sh
poetry shell
pytest -v -p no:cacheprovider tests/e2e/
```

There is a test container designed to run the e2e tests in docker-compose in a gitlab pipeline.
But this can also be executed locally to debug pipeline problems
and in case you can't or don't want to install the test dependencies locally,

`docker compose run --quiet-pull --rm test /app/.venv/bin/pytest tests/e2e -v --environment pipeline`


#### using the Tilt dev-env


Start the necessary services via tilt:
```sh
tilt up keycloak ldap-server ldap-notifier udm-rest-api stack-data-ums stack-data-swp provisioning provisioning-udm-listener
```
Limiting the tilt-resources instead of plainly running `tilt up` will save time and machine resources.

The provisioning-api and ldap-server are not accessible from the outside.
We can work around that by starting a kubernetes `port-forward`:
`kubectl port-forward provisioning-api-{pod-hash} 7777`
`kubectl port-forward ldap-server-0 3890:389`

The unit- and integration-tests are configured via ENV values.
The End to End tests are designed to also run in other environments.
(outside the provisioning repository)
That's why they are configured using pytest arguments:

```sh
Custom options:
  --provisioning-api-base-url=PROVISIONING_API_BASE_URL
                        Base URL of the UDM REST API
  --provisioning-admin-username=PROVISIONING_ADMIN_USERNAME
                        UDM admin login password
  --provisioning-admin-password=PROVISIONING_ADMIN_PASSWORD
                        UDM admin login password
  --udm-rest-api-base-url=UDM_REST_API_BASE_URL
                        Base URL of the UDM REST API
  --udm-admin-username=UDM_ADMIN_USERNAME
                        UDM admin login password
  --udm-admin-password=UDM_ADMIN_PASSWORD
                        UDM admin login password
  --ldap-server-uri=LDAP_SERVER_URI
  --ldap-host-dn=LDAP_HOST_DN
  --ldap-password=LDAP_PASSWORD
```

E.g.:

```sh
poetry shell
pytest -v -p no:cacheprovider tests/e2e/ --ldap-server-uri ldap://localhost:3890 --provisioning-admin-username admin --provisioning-admin-password provisioning
```

### Pre-commit

Run the pre-commit checks before committing:
```sh
docker compose run --rm pre-commit run
```

### Sphinx Documentation

Build the sphinx documentation:
```sh
docker compose run docs make html
```
