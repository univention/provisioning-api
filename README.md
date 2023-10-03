# Provisioning

Tooling for provisioning LDAP objects to external services.

## Components

- [Dispatcher service](./src/dispatcher/)

  The central service to receive LDAP changes and forward them to subscribed clients.

- [Core and client library](./src/core/)

  Everything needed to implement a client.

- [Example client](./src/example-client/)

  An example implementation of a client.

## Run

### Start dependencies

You can start a local Redis instance for testing:
```sh
docker compose up --detach --remove-orphans
```

This will run Redis on its standard port 6379.

The RedisInsights GUI will be served at http://localhost:8002.

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

Run tests:
```sh
poetry run pytest
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
