# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG LISTENER_BASE_IMAGE=artifacts.software-univention.de/nubus/images/listener-base
ARG LISTENER_BASE_IMAGE_TAG=0.11.0@sha256:cfb165acc8d021a9d61c2791f30dcb460d9425412821557b2b13d57a1add6b10

ARG WORKDIR="/app"

FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} as builder

ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=udm_listener
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      pipx \
      python3-venv \
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

# copy source code
COPY ./provisioning-listener/src/server ./src/server
COPY ./src/univention/provisioning/models ./src/univention/provisioning/models
COPY ./provisioning-listener/provisioning_listener ./src/provisioning_listener
COPY ./provisioning-listener/poetry.lock \
     ./provisioning-listener/pyproject.toml \
     ./

# install dependencies
RUN poetry install --only main

FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} as final

ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR} .

# Copy patch files
COPY ./docker/udm-listener/*.patch /tmp/

# Install patch utility
# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
    patch && \
    patch -p1 -i /tmp/listener.py.patch /usr/lib/python3/dist-packages/listener.py && \
    patch -p1 -i /tmp/handler_logging.py.patch /usr/lib/python3/dist-packages/univention/listener/handler_logging.py && \
    apt-get purge --auto-remove --assume-yes patch && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY ./provisioning-listener/provisioning_listener/ldap_listener.py /usr/lib/univention-directory-listener/system/

ENV PYTHONPATH=$PYTHONPATH:./src:./.venv/lib/python3.11/site-packages
