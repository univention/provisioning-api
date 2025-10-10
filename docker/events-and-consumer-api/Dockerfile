# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

###############################################
# Stage 1: build dependencies and software
FROM debian:12-slim AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11
# UV_PROJECT_ENVIRONMENT=/app

RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./rest-api/uv.lock \
  ./rest-api/pyproject.toml \
  /app/rest-api/

WORKDIR /app/rest-api
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./rest-api/src /app/rest-api/src

# Install the project in editable mode so that changes to source files in
# rest-api/src are immediately reflected in the container.
# This avoids issues with Docker build cache and ensures the venv always
# uses the latest source code.
RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev && \
  uv pip install -e .

###############################################
# Stage 3: final image
FROM gcr.io/distroless/python3-debian12:nonroot AS final

ENV PYTHONUNBUFFERED=1

COPY --from=build /app/rest-api /app/rest-api

ENTRYPOINT ["/app/rest-api/.venv/bin/rest-api"]
