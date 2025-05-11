# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11


ARG WORKDIR="/app"

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as build
ARG WORKDIR
WORKDIR ${WORKDIR}

ARG USER=fastapi
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
    # Do not ask questions
    POETRY_NO_INTERACTION=1

# install Poetry
RUN pip3 install --break-system-packages --no-cache-dir poetry==1.8.3 poetry-plugin-export==1.8.0

# copy dependencies configuration
COPY ./src/poetry.lock \
     ./src/pyproject.toml \
     ${WORKDIR}/

# export dependencies
RUN poetry export -o ${WORKDIR}/requirements.txt

###############################################
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as final
ARG WORKDIR
WORKDIR ${WORKDIR}

RUN apt-get --assume-yes --verbose-versions --no-install-recommends install 'python3-pip=23.0.*'
COPY --from=build ${WORKDIR}/pyproject.toml ${WORKDIR}/requirements.txt ${WORKDIR}/
RUN pip3 install --break-system-packages --no-cache-dir -r ${WORKDIR}/requirements.txt
COPY ./src/univention/provisioning ${WORKDIR}/univention/provisioning
RUN pip3 install --break-system-packages --no-cache-dir ${WORKDIR}/

ENTRYPOINT ["/usr/bin/python3", "-m", "univention.provisioning.consumer.example_client.main"]
