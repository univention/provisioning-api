# Unittests

This folder contains a set of unit tests which cover the behavior of the chart
`common`.


## Requirements

- `docker compose` has to be set up and working

## How to run this manually

```
# Run the test suite
docker compose run -it --rm test

# Have a shell
docker compose run -it --rm test bash
```

## Hacking on this

Currently I use a develop install in the pipenv, most likely in the wrong way:

```
cd docker/testrunner
pipenv sync
pipenv shell

# Assuming that a clone of the pytest_helm repository is at this location
pip install -e ../../../pytest_helm

pytest
```
