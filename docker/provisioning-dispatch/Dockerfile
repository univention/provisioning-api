ARG WORKDIR="/app"

###############################################
# Stage 1: build and install dependencies
FROM library/python:3.11-slim as builder
ARG WORKDIR
WORKDIR ${WORKDIR}

ENV \
    # Do not buffer `stdout`
    PYTHONUNBUFFERED=1 \
    # Do not create `.pyc` files
    PYTHONDONTWRITEBYTECODE=1 \
    # Do not ask questions
    POETRY_NO_INTERACTION=1 \
    # Put .venv inside source folder
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    # Cache of poetry
    POETRY_CACHE_DIR=/tmp/poetry_cache

# copy source code
COPY ./src ${WORKDIR}/src
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/

RUN \
    # install Poetry
    pip install --no-cache-dir poetry==1.6.1 && \
    # install dependencies
    poetry install --only main

###############################################
# Stage 2: test image
from builder as test

RUN poetry install --with dev

###############################################
# Stage 2: final image
FROM library/python:3.11-slim as final
ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR} ${WORKDIR}

EXPOSE 7777

# run
ENTRYPOINT [ \
        "./.venv/bin/python3", "-m", \
        "uvicorn", "consumer:start_dev", \
        "--log-config", "logging.yaml", \
        "--host", "0.0.0.0", \
        "--port", "7777" \
    ]
