# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

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
  UV_PYTHON=python3.13

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./dispatcher/uv.lock \
  ./dispatcher/pyproject.toml \
  /app/dispatcher/

WORKDIR /app/dispatcher
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./dispatcher/src /app/dispatcher/src

# Install the project in editable mode so that changes to source files in
# dispatcher/src are immediately reflected in the container.
# This avoids issues with Docker build cache and ensures the venv always
# uses the latest source code.
RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev && \
  uv pip install -e .


###############################################
# Stage 3: final image
#
# Distroless: no shell, so no RUN steps here. The user, os-release and CA
# bundle come from the base image.
FROM ${UCS_DISTROLESS_IMAGE}:${UCS_DISTROLESS_IMAGE_TAG} AS final

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/dispatcher/.venv/bin:$PATH

COPY --from=build /app/dispatcher /app/dispatcher
WORKDIR /app/dispatcher
ENTRYPOINT [ "/app/dispatcher/.venv/bin/dispatcher" ]
