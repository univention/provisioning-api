# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG LISTENER_BASE_IMAGE_TAG=v0.4.1
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base
ARG PYTHON_IMAGE_VERSION=3.7
ARG UDM_REST_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-udm-rest/udm-rest-api
ARG UDM_REST_IMAGE_TAG=latest

FROM library/python:${PYTHON_IMAGE_VERSION}-slim as builder1
WORKDIR /app

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
COPY ./src ./src
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ./

RUN \
    # install Poetry
    pip install --no-cache-dir poetry==1.5.1 && \
    # install dependencies \
    poetry config installer.max-workers 10 && \
    poetry install --only main --no-ansi -vvv

############################################### \

from builder1 as test

RUN poetry install --with dev


FROM ${UDM_REST_IMAGE}:${UDM_REST_IMAGE_TAG} as builder2


FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} as final
ARG PYTHON_IMAGE_VERSION

WORKDIR /app
COPY --from=builder1 /app .
COPY --from=builder2 usr/lib/python3/dist-packages /usr/lib/python3/dist-packages

COPY ./src/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/

ENV PYTHONPATH=$PYTHONPATH:./src:./.venv/lib/python${PYTHON_IMAGE_VERSION}/site-packages