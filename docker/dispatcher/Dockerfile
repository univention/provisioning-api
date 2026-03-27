# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

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
  UV_PYTHON=python3.11

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
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/dispatcher/.venv/bin:$PATH

ARG USER=dispatcher
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
  rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
  groupadd -r ${USER} -g 1000 && \
  useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/dispatcher /app/dispatcher

USER ${USER}

CMD ["dispatcher"]

RUN \
  python3.11 -V && \
  python3.11 -m site && \
  python3.11 -c 'import univention.provisioning.dispatcher.main'
