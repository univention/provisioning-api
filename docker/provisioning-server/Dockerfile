# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

# One image for the four Python services (api, dispatcher, prefill,
# udm-transformer). They share almost all of their dependencies, so four
# separate images multiplied the same packages across four SBOMs. Select the
# process with the container command; see docs/simplify/README.md (W2).

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_DISTROLESS_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-distroless-python-530
# TODO: repoint to the 5.3.0-build.<date> tag once ucs-base-image!109 is merged
ARG UCS_DISTROLESS_IMAGE_TAG=0.24.0-pre-mmeschter-distroless-python@sha256:074d9c80454289f0b0f6adba72b58d0259019fe595ecd6485624331d87731376
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
  UV_PROJECT_ENVIRONMENT=/app/.venv

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
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    --no-install-workspace && \
  uv export --no-dev --frozen --no-emit-workspace --no-hashes \
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    -o /app/requirements.txt

# copy source code
COPY ./backends/src /app/backends/src
COPY ./common/src /app/common/src
COPY ./dispatcher/src /app/dispatcher/src
COPY ./prefill/src /app/prefill/src
COPY ./rest-api/src /app/rest-api/src
COPY ./udm-transformer/src /app/udm-transformer/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    --no-editable

# Verify every entrypoint imports while a shell is still available; the final
# stage has none. rest-api reads its settings at import time, hence the env.
RUN \
  /app/.venv/bin/python -c 'import univention.provisioning.dispatcher.main' && \
  /app/.venv/bin/python -c 'import univention.provisioning.prefill.main' && \
  /app/.venv/bin/python -c 'import univention.provisioning.udm_transformer.main' && \
  LOG_LEVEL=DEBUG DEBUG=false ROOT_PATH=/ CORS_ALL=false \
  ADMIN_USERNAME=x ADMIN_PASSWORD=x NATS_USER=x NATS_PASSWORD=x NATS_HOST=x NATS_PORT=1 \
  ADMIN_NATS_USER=x ADMIN_NATS_PASSWORD=x PREFILL_USERNAME=x PREFILL_PASSWORD=x \
  EVENTS_USERNAME_UDM=x EVENTS_PASSWORD_UDM=x \
  /app/.venv/bin/python -c 'import univention.provisioning.rest.main'

###############################################
# Stage 2: final image
#
# Distroless: no shell, so no RUN steps here. The user, os-release and CA
# bundle come from the base image.
FROM ${UCS_DISTROLESS_IMAGE}:${UCS_DISTROLESS_IMAGE_TAG} AS final

EXPOSE 7777

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/.venv/bin:$PATH

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/requirements.txt /app/requirements.txt

WORKDIR /app

# No default process: the base image's ENTRYPOINT is reset and no CMD is set, so
# every caller has to name the service it wants (see helm values / compose).
ENTRYPOINT []
