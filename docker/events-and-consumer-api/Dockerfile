# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.10.0
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520


ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as build
ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=fastapi
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=23.* \
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
COPY ./src ${WORKDIR}/src
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/

RUN \
    # install Poetry
    pip3 install --break-system-packages --no-cache-dir poetry==1.6.1 && \
    # install dependencies
    poetry install --only main

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

EXPOSE 7777

# run
ENTRYPOINT [ \
        "./.venv/bin/uvicorn", \
         "app.main:app", \
        "--log-config", "logging.yaml", \
        "--host", "0.0.0.0", \
        "--port", "7777" \
    ]
