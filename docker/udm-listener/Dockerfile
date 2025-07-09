# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG LISTENER_BASE_IMAGE=artifacts.software-univention.de/nubus/images/listener-base
ARG LISTENER_BASE_IMAGE_TAG=0.12.1@sha256:73251fdc47cda8b7c4fea70b73457eab8a95d394fdab7ad3f1ffbd5bab273740

###############################################
# Stage 1: build dependencies and software
FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS build

SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.11
# UV_PROJECT_ENVIRONMENT=/app

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./listener/uv.lock \
  ./listener/pyproject.toml \
  /app/listener/

WORKDIR /app/listener
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
  --locked \
  --no-dev \
  --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./listener/src /app/listener/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable

###############################################
# Stage 2: final image
FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY ./docker/udm-listener/*.patch /tmp/
# Install patch utility
RUN apt-get update && \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  patch && \
  patch -p1 -i /tmp/listener.py.patch /usr/lib/python3/dist-packages/listener.py && \
  patch -p1 -i /tmp/handler_logging.py.patch /usr/lib/python3/dist-packages/univention/listener/handler_logging.py && \
  apt-get purge --auto-remove --assume-yes patch && \
  rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* && \
  cp /usr/sbin/univention-directory-listener /usr/bin

ENV PYTHONUNBUFFERED=1 \
  PYTHONPATH=/app/listener/.venv/lib/python3.11/site-packages

COPY ./listener/src/ldap_listener.py /usr/lib/univention-directory-listener/system/
COPY ./docker/udm-listener/univention-directory-listener /usr/sbin/univention-directory-listener

# TODO: Fix docker compose so that it runs without root
# ARG USER=udm-listener
# RUN groupadd -r ${USER} -g 1000 && \
#     useradd -r -d /app -g ${USER} -N ${USER} -u 1000
#
# COPY --from=build --chown=${USER}:${USER} /app/listener /app/listener
COPY --from=build /app/listener /app/listener

USER ${USER}
#
# RUN \
#   python3.11 -V && \
#   python3.11 -m site && \
#   python3.11 -c 'import univention.provisioning.listener'
