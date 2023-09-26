###############################################
# Stage 1: build and install dependencies
FROM library/python:3.11-slim as builder
ARG WORKDIR

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
WORKDIR /app
RUN echo $WORKDIR && ls && pwd
COPY . .

# install Poetry
RUN pip install --no-cache-dir poetry==1.6.1 && \
    poetry install --only main


###############################################
# Stage 2: final image
FROM library/python:3.11-slim as final

COPY --from=builder /app /

EXPOSE 7777

# run
ENTRYPOINT [ \
        "./.venv/bin/python", "-m", \
        "uvicorn", "dispatcher:start_dev", \
        "--log-config", "logging.yaml", \
        "--host", "0.0.0.0", \
        "--port", "7777" \
    ]
