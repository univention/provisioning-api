# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG LISTENER_BASE_IMAGE_TAG=v0.4.1
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base
ARG UDM_REST_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/udm-rest-api
ARG UDM_REST_IMAGE_TAG=latest

ARG WORKDIR="/app"

FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} as builder

ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=udm_listener
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=18.1-5 curl=7.64.0-4+deb10u8 \
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

# copy source code
COPY ./src/server ./src/server
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ./
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.5.1 python3 -
RUN poetry install --with dev


FROM ${UDM_REST_IMAGE}:${UDM_REST_IMAGE_TAG} as udm_rest_image


FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} as final

ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=builder ${WORKDIR} .
COPY --from=udm_rest_image /usr/lib/python3/dist-packages /usr/lib/python3/dist-packages

COPY ./src/server/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/

ENV PYTHONPATH=$PYTHONPATH:./src/server:./.venv/lib/python3.7/site-packages
