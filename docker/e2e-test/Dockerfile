# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.5-build.20260417@sha256:83a3b0eef92fd907fa8ec188792e607bc2d3e3a9ad0cc21e39981b728f4c98dd

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /usr/local/bin/uv

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
