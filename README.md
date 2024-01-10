# Disclaimer - Work in progress

The repository you are looking into is work in progress.

It contains proof of concept and preview builds in development created in context of the openDesk project.

The repository's content provides you with first insights into the containerized cloud IAM from Univention, derived from the UCS appliance.

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

### Start dependencies

You can start a local NATS instance for testing:
```sh
docker compose up --detach --remove-orphans nats
```

This will run NATS on its standard port 4222.

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

Run the server in development mode (i.e. with hot-reloading):
```sh
poetry run dev
```
The server is available on port 7777.
Find the OpenAPI schema here: http://localhost:7777/docs .

## Tests

If you want to run integration tests, make sure, you run

```sh
docker compose run nats
```

first. Then:

```sh
poetry run pytest <dir/of/test-subset>
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
