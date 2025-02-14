# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11

###############################################
# Stage 1: Install software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS app_builder

ARG USER=dispatcher
ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11
    # UV_PROJECT_ENVIRONMENT=/app

RUN apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3 \
    && rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

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
    --no-install-project

# copy source code
COPY ./dispatcher/src /app/dispatcher/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable

RUN groupadd -r ${USER} -g 1000 && \
    useradd -r -d /app -g ${USER} -N ${USER} -u 1000

USER ${USER}


CMD ["/app/.venv/bin/python3", "-m", "univention.provisioning.dispatcher.main"]

RUN \
  .venv/bin/python3.11 -V && \
  .venv/bin/python3.11 -m site && \
  .venv/bin/python3.11 -c 'import univention.provisioning.dispatcher.main'

###############################################
# Stage 2: Remove uv cache
# TODO:
