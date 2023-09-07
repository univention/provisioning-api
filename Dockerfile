FROM library/python:3.9-slim as base

# install Poetry
ARG POETRY_HOME=/opt/poetry
RUN python3 -m venv ${POETRY_HOME} && \
    ${POETRY_HOME}/bin/pip install poetry=1.6.1 && \
    ${POETRY_HOME}/bin/poetry --version

# copy source code
WORKDIR /app
COPY ./server/ /app
COPY logging.yaml poetry.lock pyproject.toml /app/

# install dependencies
RUN poetry install

# run
ENTRYPOINT [ \
        "poetry", "run", \
        "uvicorn", "server.main:app", \
        "--log-config", "logging.yaml", \
        "--host", "0.0.0.0", \
        "--port", "7777" \
    ]
