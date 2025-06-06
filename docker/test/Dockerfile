# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11


ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as build
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip \
      python3-univention-directory-manager-rest-client \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

ENV \
    WEB_CONCURRENCY=1 \
    # Do not buffer `stdout`
    PYTHONUNBUFFERED=1 \
    # Do not create `.pyc` files
    PYTHONDONTWRITEBYTECODE=1 \
    # Do not exceed connection pool
    POETRY_INSTALLER_MAX_WORKERS=5 \
    # Do not ask questions
    POETRY_NO_INTERACTION=1 \
    # Put .venv inside source folder
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    # Cache of poetry
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    # Include system site packages
    PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages/

# install Poetry
RUN pip3 install --break-system-packages --no-cache-dir poetry==1.6.1

# install dependencies
COPY poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/
RUN poetry install --no-root

# copy source code
COPY ./src/server ${WORKDIR}/src/server
COPY ./src/univention/provisioning ${WORKDIR}/src/univention/provisioning
COPY ./tests ${WORKDIR}/tests/
RUN poetry install --with dev
