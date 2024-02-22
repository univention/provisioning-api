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

Make sure you run

```sh
docker compose up --detach --remove-orphans
```

first, then

```sh
python tests/e2e/end_2_end.py
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
