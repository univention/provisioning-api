# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

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
    PATH=/app/e2e_tests/.venv/bin:$PATH

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./consumer /app/consumer

# e2e_tests is not a workspace member and keeps its own lock, but it path-depends
# on members whose manifests say `workspace = true`. Those only resolve if the
# workspace root and every member manifest are discoverable from here.
COPY ./pyproject.toml /app/
COPY ./consumer_example/pyproject.toml /app/consumer_example/
COPY ./dispatcher/pyproject.toml /app/dispatcher/
COPY ./prefill/pyproject.toml /app/prefill/
COPY ./rest-api/pyproject.toml /app/rest-api/
COPY ./udm-transformer/pyproject.toml /app/udm-transformer/

COPY ./e2e_tests/uv.lock \
     ./e2e_tests/pyproject.toml \
     /app/e2e_tests/

WORKDIR /app/e2e_tests
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
    --locked \
    --no-install-project

COPY ./e2e_tests/tests /app/e2e_tests/tests
