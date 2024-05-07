# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.12
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

ARG WORKDIR="/app"

FROM ${UDM_REST_IMAGE}:${UDM_REST_IMAGE_TAG} as udm_rest_image

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as build
ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=udm-transformer
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get -qq update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=23.* \
      python3-univention-directory-manager-rest=12.0* \
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

# copy source code
COPY ./src/server ${WORKDIR}/src/server
COPY ./src/shared ${WORKDIR}/src/shared
COPY ./src/udm_transformer ${WORKDIR}/src/udm_transformer
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/

    # Activate system packages to get the debian installed udm library
RUN poetry config virtualenvs.options.system-site-packages true && \
    # install dependencies
    poetry install --only main

###############################################
# Stage 2: final image
FROM build as final
ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=build ${WORKDIR} ${WORKDIR}

# run
ENTRYPOINT ["/bin/bash", "-c", "./.venv/bin/python3 src/udm_transformer/main.py"]
