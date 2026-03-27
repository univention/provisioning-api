# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.5-build.20260326@sha256:163d393824d089e4d33b97378819e319627dea6e183d33200ac54ac1211614f0

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.2@sha256:c4f5de312ee66d46810635ffc5df34a1973ba753e7241ce3a08ef979ddd7bea5 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
    PYTHONUNBUFFERED=1 \
    PATH=/app/e2e_tests/.venv/bin:$PATH


COPY ./backends /app/backends
COPY ./common /app/common
COPY ./consumer /app/consumer
COPY ./e2e_tests/uv.lock \
     ./e2e_tests/pyproject.toml \
     /app/e2e_tests/

WORKDIR /app/e2e_tests
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
    --locked \
    --no-install-project

COPY ./e2e_tests/tests /app/e2e_tests/tests
