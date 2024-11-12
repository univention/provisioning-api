# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11

##############################################################
# Optimized for fast rebuilds (when only tests/* is changed) #
##############################################################

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS dep_builder

ARG WORKDIR="/app"

ENV \
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

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR ${WORKDIR}

RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip=23.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir poetry==1.8.3 poetry-plugin-export==1.8.0 \
    && poetry config virtualenvs.create false \
    && poetry config warnings.export false

# copy dependencies source code
COPY ./CHANGELOG.md ${WORKDIR}
COPY ./backends ${WORKDIR}/backends/
COPY ./common ${WORKDIR}/common/
COPY ./consumer ${WORKDIR}/consumer/
COPY ./consumer_example ${WORKDIR}/consumer_example/
COPY ./dispatcher ${WORKDIR}/dispatcher/
COPY ./prefill ${WORKDIR}/prefill/
COPY ./rest-api ${WORKDIR}/rest-api/
COPY ./udm-transformer ${WORKDIR}/udm-transformer/
COPY ./tests ${WORKDIR}/tests/
COPY ./pyproject.toml ./poetry.lock ${WORKDIR}/

RUN poetry install --with dev
