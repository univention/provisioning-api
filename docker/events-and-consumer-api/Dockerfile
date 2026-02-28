# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.4-build.20260224@sha256:b3ec1d42122f836a2c4a08793eeb5be868459e450501fdebbc60fcbadd7824e5

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.10.7@sha256:edd1fd89f3e5b005814cc8f777610445d7b7e3ed05361f9ddfae67bebfe8456a /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11
# UV_PROJECT_ENVIRONMENT=/app

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./rest-api/uv.lock \
  ./rest-api/pyproject.toml \
  /app/rest-api/

WORKDIR /app/rest-api
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./rest-api/src /app/rest-api/src

# Install the project in editable mode so that changes to source files in
# rest-api/src are immediately reflected in the container.
# This avoids issues with Docker build cache and ensures the venv always
# uses the latest source code.
RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev && \
  uv pip install -e .

###############################################
# Stage 3: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/rest-api/.venv/bin:$PATH

ARG USER=rest-api
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
  rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
  groupadd -r ${USER} -g 1000 && \
  useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/rest-api /app/rest-api

USER ${USER}

CMD ["rest-api"]

RUN \
  python3.11 -V && \
  python3.11 -m site && \
  python3.11 -c 'import univention.provisioning.rest'
# TODO: importing main executes code
# python3.11 -c 'import univention.provisioning.rest.main'
