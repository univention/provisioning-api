# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260911@sha256:51466e4d602f2ab8c4e8dcbb1d174b00bdb8e738ca9c999b0bd0627be59aaff4
ARG UCS_DISTROLESS_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-distroless-python
ARG UCS_DISTROLESS_IMAGE_TAG=5.3.0-build.20260917@sha256:a965bfba1bb1af8cf0c47d6e436c8a37aaa26ed15b29c9b55636839b2b8436e3

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/app/consumer_example/.venv

# uv needs every workspace member's manifest to load the workspace, including
# members this image does not install.
COPY ./pyproject.toml ./uv.lock /app/
COPY ./backends/pyproject.toml /app/backends/
COPY ./common/pyproject.toml /app/common/
COPY ./consumer/pyproject.toml /app/consumer/
COPY ./consumer_example/pyproject.toml /app/consumer_example/
COPY ./dispatcher/pyproject.toml /app/dispatcher/
COPY ./prefill/pyproject.toml /app/prefill/
COPY ./rest-api/pyproject.toml /app/rest-api/
COPY ./udm-transformer/pyproject.toml /app/udm-transformer/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --package nubus-provisioning-consumer-example \
    --no-install-workspace && \
  uv export --no-dev --frozen --no-emit-workspace --no-hashes \
    --package nubus-provisioning-consumer-example -o /app/consumer_example/requirements.txt

# copy source code
COPY ./common/src /app/common/src
COPY ./consumer/src /app/consumer/src
COPY ./consumer_example/src /app/consumer_example/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --package nubus-provisioning-consumer-example --no-editable

# Verify the entrypoint imports while a shell is still available; the final
# stage has none.
RUN \
  /app/consumer_example/.venv/bin/python -c 'import univention.provisioning.consumer_example.main'

###############################################
# Stage 2: final image
#
# Distroless: no shell, so no RUN steps here. The user, os-release and CA
# bundle come from the base image.
FROM ${UCS_DISTROLESS_IMAGE}:${UCS_DISTROLESS_IMAGE_TAG} AS final

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/consumer_example/.venv/bin:$PATH

COPY --from=build /app/consumer_example /app/consumer_example

WORKDIR /app

# The base image sets an ENTRYPOINT of its own; reset it so that CMD is the
# whole command line.
ENTRYPOINT []
CMD ["consumer_example"]
