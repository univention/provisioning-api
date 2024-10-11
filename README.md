# Provisioning

Nubus component for provisioning LDAP objects to external services.

See [Nubus for Kubernetes - Architecture Manual](https://docs.software-univention.de/nubus-kubernetes-architecture/latest/en/components/provisioning-service.html) for an in-depth explanation.

## Sub projects

This repository contains multiple Poetry projects.
Each one has its own README.md.
Click on the name in the following list, to navigate to it:

- [backends](backends/README.md): database backend code (MQ and KV)
- [common](common/README.md): shared code
- [consumer](consumer/README.md): provisioning consumer library
- [consumer_example](consumer_example/README.md): example implementation of a consumer
- [dispatcher](dispatcher/README.md): service that distributes incoming events to subscribed consumers
- [listener](listener/README.md): LDAP change event generation source (temporary, until _LDIF Producer_ takes over)
- [prefill](prefill/README.md): service to synthesize event data for consumer initialization
- [rest-api](rest-api/README.md): REST APIs for consumers
- [udm-transformer](udm-transformer/README.md): service to transform LDAP objects to UDM objects

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

#### Problems building 'tests' container

If you encounter conflicting dependencies building the `tests` container, update all Poetry lock files:

```shell
for DIR in backends common consumer consumer_example dispatcher listener prefill rest-api tests udm-transformer; do (cd $DIR && . .venv/bin/activate && poetry update; deactivate); done
```

### Create a Subscription
To create a subscription, open http://localhost:7777/docs and find the method called 'Create Subscription'.
Enter the following data into the request body:

```sh
{
  "name": "subscription1",
  "realms_topics": [{"realm": "udm", "topic": "groups/group"}],
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

### Unit tests

```sh
poetry run pytest tests/unit
```
or
```shell
python3 -m pytest tests/unit
```

### Integration tests

```shell
docker compose run --quiet-pull --rm test /app/.venv/bin/python3 -m pytest tests/integration
```

### E2E tests
#### Setup

Copy the example e2e test settings json file:
```sh
cp tests/e2e/e2e_settings.json.example tests/e2e/e2e_settings.json
```

The json file includes all parameters, including credentials
for the "local", "dev-env" and "pipeline" environments.
This is acceptable because these environments are only run locally and never exposed publicly.
Because the "gaia" environment is publicly available
we don't put the real credentials for it into the tests/e2e/e2e_settings.json file.

To also run the tests against a gaia deployment,
you need to change all `"changeme"` entries in the `tests/e2e/e2e_settings.json`
to their correct values.

#### Using docker compose

First, start the provisioning-components:

```sh
docker compose up --detach --remove-orphans
```

optimized command:

```sh
docker compose up --pull always --build events-and-consumer-api nats1 nats2 nats3 dispatcher prefill udm-listener udm-transformer ldap-notifier udm-rest-api ldap-server
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

#### Using the Tilt dev-env


Start the necessary services via tilt:

```sh
tilt up keycloak ldap-server ldap-notifier udm-rest-api stack-data-ums stack-data-swp provisioning provisioning-udm-listener
```

Limiting the tilt-resources instead of plainly running `tilt up` will save time and machine resources.

The provisioning-api and ldap-server are not accessible from the outside.
We can work around that by starting a kubernetes `port-forward`:
`kubectl port-forward deploy/provisioning-api 7777`
`kubectl port-forward ldap-server-0 3890:389`

The unit- and integration-tests are configured via ENV values.
The End to End tests are designed to also run in other environments.
(outside the provisioning repository)

the well-known configuration-values for the e2e tests are configured in
`tests/e2e/conftest.py`

you can specify the environment via a pytest argument:

```sh
--environment=ENVIRONMENT
                      set the environment you are running the tests
                      in.accepted values are: 'local', 'dev-env', 'pipeline'
                      and 'gaia'
```

E.g.:

```sh
poetry shell
pytest -v -p no:cacheprovider tests/e2e/ --environment dev-env

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
