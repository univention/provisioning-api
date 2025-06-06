# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11


ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as build
ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=dispatcher
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip \
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
RUN pip3 install --break-system-packages --no-cache-dir poetry==1.6.1

# install dependencies
COPY poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/
RUN poetry install --no-root

# copy source code
COPY ./src/server ${WORKDIR}/src/server
COPY ./src/univention/provisioning/models ${WORKDIR}/src/univention/provisioning/models
RUN poetry install --only main

###############################################
# Stage 2: test image
FROM build as test

RUN poetry install --with dev

###############################################
# Stage 2: final image
FROM build as final
ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=build ${WORKDIR} ${WORKDIR}

# run
ENTRYPOINT ["./.venv/bin/python3", "-m", "server.core.dispatcher.main"]
