# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260825@sha256:f4b3ef96d03c574c5c3f57d4d41945a911ef05d63ca50718989b593c5d9cb6be

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    PYTHONUNBUFFERED=1 \
    PATH=/app/.venv/bin:$PATH

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./consumer /app/consumer
COPY ./consumer_example /app/consumer_example
COPY ./dispatcher /app/dispatcher
COPY ./listener /app/listener
COPY ./prefill /app/prefill
COPY ./rest-api /app/rest-api
COPY ./udm-transformer /app/udm-transformer
COPY ./tests/test_helpers /app/tests/test_helpers

COPY ./uv.lock \
     ./pyproject.toml \
     ./README.md \
     /app/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
    --locked
