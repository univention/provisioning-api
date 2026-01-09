# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.4-build.20260108@sha256:aa219aca5425e467afa8cf3a1eabb2023afa50149702da67402bf65f544cd784

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11 \
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
