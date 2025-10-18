# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.2-build.20250828@sha256:2523fd15d25ab590918309b538510b7bd26b92ba8bed89587381ac8c3c62d324

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11

# copy dependencies
COPY ./common /app/common
COPY ./consumer /app/consumer
COPY ./consumer_example/uv.lock \
     ./consumer_example/pyproject.toml \
     /app/consumer_example/

WORKDIR /app/consumer_example
# install dependencies except univention.provisioning.*
# as mixing namespace packages editable and non-editable causes issues
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-package nubus-provisioning-common \
  --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./consumer_example/src /app/consumer_example/src

# Install the project in editable mode so that changes to source files in
# dispatcher/src are immediately reflected in the container.
# This avoids issues with Docker build cache and ensures the venv always
# uses the latest source code.
RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev

###############################################
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/consumer_example/.venv/bin:$PATH

ARG USER=consumer_example
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
  rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
  groupadd -r ${USER} -g 1000 && \
  useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app /app

USER ${USER}

CMD ["consumer_example"]

RUN \
  python3 -V && \
  python3 -m site && \
  python3 -c 'import univention.provisioning.models' && \
  python3 -c 'import univention.provisioning.consumer_example.main'
