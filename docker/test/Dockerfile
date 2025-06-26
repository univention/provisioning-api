# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-522
ARG UCS_BASE_IMAGE_TAG=0.18.2-build-2025-06-12

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS test
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

############################################################
# Stage 2: image for merging coverage results and reporting

FROM test AS coverage

RUN mkdir -pv /coverage
VOLUME /coverage

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-editable

COPY ./listener/src/ldap_listener.py /usr/lib/univention-directory-listener/system/
COPY ./docker/test/coverage_reports ./docker/test/fix_e2e_coverage_xml /usr/local/bin/
RUN chmod 755 /usr/local/bin/*

WORKDIR /app/.venv/lib/python3.11/site-packages

CMD ["/usr/local/bin/coverage_reports"]
