ARG LISTENER_BASE_IMAGE_TAG=v0.4.1
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base:${LISTENER_BASE_IMAGE_TAG}

# hadolint ignore=DL3006
FROM library/python:3.11-slim as builder
ARG WORKDIR="/app"

ARG WORKDIR
WORKDIR ${WORKDIR}

# copy source code
COPY ./src ${WORKDIR}/src
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/

RUN \
    # install Poetry
    pip install --no-cache-dir poetry==1.6.1 && \
    # install dependencies
    poetry install --only main

###############################################
# Stage 2: test image
from builder as test

RUN poetry install --with dev

FROM ${LISTENER_BASE_IMAGE} as final
WORKDIR /app

COPY ./src/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/
COPY ./src ./
ENV PYTHONPATH=$PYTHONPATH:/app
