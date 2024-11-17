# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.13.1-post-main-build-2024-09-09
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
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

# install Poetry
RUN pip3 install --break-system-packages --no-cache-dir poetry==1.6.1

# install dependencies
COPY --chown=${USER}:${USER} ./backends ${WORKDIR}/backends/
COPY --chown=${USER}:${USER} ./consumer ${WORKDIR}/consumer/
COPY --chown=${USER}:${USER} rest-api/poetry.lock \
     rest-api/pyproject.toml \
     rest-api/README.md \
     ${WORKDIR}/rest-api/

WORKDIR ${WORKDIR}/rest-api/
RUN poetry install --no-root

# copy source code
COPY --chown=${USER}:${USER} ./rest-api ${WORKDIR}/rest-api/
RUN poetry install --only main

###############################################
# Stage 2: final image
FROM build AS final
ARG WORKDIR
WORKDIR ${WORKDIR}/rest-api/

COPY --from=build ${WORKDIR} ${WORKDIR}

EXPOSE 7777
ENTRYPOINT [ \
    "./.venv/bin/uvicorn", \
    "univention.provisioning.rest.main:app", \
    "--host", "0.0.0.0", \
    "--port", "7777" \
]
