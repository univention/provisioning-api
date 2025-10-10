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
COPY ./prefill/uv.lock \
     ./prefill/pyproject.toml \
     /app/prefill/

WORKDIR /app/prefill
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./prefill/src /app/prefill/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable

###############################################
# Stage 3: final image
FROM gcr.io/distroless/python3-debian12:nonroot AS final

ENV PYTHONUNBUFFERED=1

COPY --from=build /app/prefill /app/prefill

ENTRYPOINT ["/app/prefill/.venv/bin/prefill"]
