# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.13.1-post-main-build-2024-09-09
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=consumer_example
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
COPY --chown=${USER}:${USER} ./consumer ${WORKDIR}/consumer/
COPY --chown=${USER}:${USER} consumer_example/poetry.lock \
     consumer_example/pyproject.toml \
     consumer_example/README.md \
     ${WORKDIR}/consumer_example/

WORKDIR ${WORKDIR}/consumer_example/
RUN poetry install --no-root

# copy source code
COPY --chown=${USER}:${USER} ./consumer_example ${WORKDIR}/consumer_example/
RUN poetry install --only main

###############################################
# Stage 2: final image
FROM build AS final
ARG WORKDIR
WORKDIR ${WORKDIR}/consumer_example/

COPY --from=build ${WORKDIR} ${WORKDIR}

ENTRYPOINT ["python3", "-m", "univention.provisioning.consumer_example.main"]
