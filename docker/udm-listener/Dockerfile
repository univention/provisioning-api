# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG LISTENER_BASE_IMAGE_TAG=0.8.0
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base

ARG WORKDIR="/app"

FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS builder

ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=udm_listener
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      pipx=0.12.1.0-1 \
      python3-venv=3.7.3-1 \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*
USER "$USER"

ENV \
    PATH="/home/${USER}/.local/bin:${PATH}" \
    PYTHONPATH="." \
    WEB_CONCURRENCY=1 \
    # Do not buffer `stdout`
    PYTHONUNBUFFERED=1 \
    # Do not create `.pyc` files
    PYTHONDONTWRITEBYTECODE=1 \
    # Do not ask questions
    POETRY_NO_INTERACTION=1 \
    # Put .venv inside source folder
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    # Cache of poetry
    POETRY_CACHE_DIR=/tmp/poetry_cache

# install Poetry
RUN pipx install poetry==1.5.1

# install dependencies
COPY --chown=${USER}:${USER} ./backends ${WORKDIR}/backends/
COPY --chown=${USER}:${USER} ./consumer ${WORKDIR}/consumer/
COPY --chown=${USER}:${USER} listener/poetry.lock \
     listener/pyproject.toml \
     listener/README.md \
     ${WORKDIR}/listener/

WORKDIR ${WORKDIR}/listener/
RUN poetry install --no-root

# copy source code
COPY --chown=${USER}:${USER} ./listener ${WORKDIR}/listener/

FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS final

ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR} .

# Copy patch files
COPY ./docker/udm-listener/*.patch /tmp/

# patch univention-listener modules to not write to filesystem
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
    patch && \
    patch -p1 -i /tmp/listener.py.patch /usr/lib/python3/dist-packages/listener.py && \
    patch -p1 -i /tmp/handler_logging.py.patch /usr/lib/python3/dist-packages/univention/listener/handler_logging.py && \
    apt-get purge --auto-remove --assume-yes patch && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY ./listener/src/ldap_listener.py /usr/lib/univention-directory-listener/system/

ENV PYTHONPATH=./listener/src:./listener/.venv/lib/python3.7/site-packages
