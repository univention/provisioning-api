# Provisioning

Tooling for provisioning LDAP objects to external services.

## Components

- [Dispatcher service](./src/dispatcher/)

  The central service to receive LDAP changes and forward them to subscribed clients.

- [Core and client library](src/shared/)

  Everything needed to implement a client.

- [Example client](./src/example-client/)

  An example implementation of a client.

## Run
Be sure you have access to gitregistry.knut.univention.de

### Start dependencies

Build container for testing:
```sh
docker compose build
```
Run container:

```sh
docker compose up --detach --remove-orphans
```


### Locally

Ensure that you have [`poetry`](https://python-poetry.org/docs/) installed.

If desired, set poetry to create a virtualenv in the project directory:
```sh
poetry config virtualenvs.in-project true
```

Install the dependencies:
```sh
poetry install --with dev
```

If you want to run Consumer Server in development mode (i.e. with hot-reloading):
```sh
poetry run dev
```
The server is available on port 7777.
Find the OpenAPI schema here: http://localhost:7777/docs .

## Integration and E2E Tests

If you want to run integration tests, make sure poetry and container are running.

```sh
poetry run pytest <dir/of/test-subset>
```
If you want to run only E2E test:

```sh
python tests/e2e/end_2_end.py
```
## MVP Tests
Be sure your container is working.

### Step 1:
Run openAPI http://localhost:7777/docs There you can create subscription /subscriptions/v1/subscription/

### Step 2:
Run http://localhost:8001/ to trigger LDAP.

Enter with:
  - **Username:** cn=admin,dc=univention-organization,dc=intranet
  - **Password:** univention

Make object changes in LDAP. E.g. press **create new entry here** and create a new object.

### Step 3:
To check if message is received by subscriber check it in OpenAPI with a method Get Subscription Messages  /messages/v1/subscription/{name}/message


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
