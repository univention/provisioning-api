# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG LISTENER_BASE_IMAGE_TAG=0.9.0-pre-cgarcia-ucs-base-2024-12-12
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base

###############################################
# Stage 1: build dependencies and software
FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS builder

ARG WORKDIR="/app"
ENV POETRY_NO_INTERACTION=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR ${WORKDIR}

ARG USER=udm_listener
RUN useradd -m "$USER"
RUN chown "$USER":"$USER" "$WORKDIR" \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      pipx \
      python3-venv \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && python3 -m pip install --no-cache-dir poetry==1.5.1 \
    && poetry config virtualenvs.create false
USER "$USER"

# copy source code
COPY ./CHANGELOG.md /tmp/
COPY ./backends ${WORKDIR}/backends/
COPY ./common ${WORKDIR}/common/
COPY ./listener ${WORKDIR}/listener/

# build wheels of dependencies and project
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' /tmp/CHANGELOG.md | tr -d '#[] ')" \
    && poetry version "$VERSION" -C ${WORKDIR}/common \
    && poetry version "$VERSION" -C ${WORKDIR}/backends \
    && poetry version "$VERSION" -C ${WORKDIR}/listener \
    && poetry build --format=wheel -C ${WORKDIR}/common \
    && poetry build --format=wheel -C ${WORKDIR}/backends \
    && poetry build --format=wheel -C ${WORKDIR}/listener

###############################################
# Stage 2: install dependencies and software, final image
FROM ${LISTENER_BASE_IMAGE}:${LISTENER_BASE_IMAGE_TAG} AS final

ARG USER=udm_listener
ARG WORKDIR="/app"
ENV WEB_CONCURRENCY=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR ${WORKDIR}

# patch univention-listener modules to not write to filesystem
COPY ./docker/udm-listener/*.patch /tmp/
RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=18.1-5 \
      patch=2.7.6-3+deb10u1 \
    && patch -p1 -i /tmp/listener.py.patch /usr/lib/python3/dist-packages/listener.py \
    && patch -p1 -i /tmp/handler_logging.py.patch /usr/lib/python3/dist-packages/univention/listener/handler_logging.py \
    && apt-get purge --auto-remove --assume-yes patch \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

# install Python dependencies, and listener module
COPY --from=builder ${WORKDIR}/*/dist/*.whl /tmp
COPY ./listener/src/ldap_listener.py /usr/lib/univention-directory-listener/system/
RUN useradd -m "$USER" \
    && chown "$USER":"$USER" "$WORKDIR" \
    && python3 -m pip install --no-cache-dir -U pip==24.0 \
    && python3 -m pip install --no-cache-dir -U /tmp/nubus_provisioning_common-*.whl \
    && python3 -m pip install --no-cache-dir -U /tmp/nubus_provisioning_backends-*.whl \
    && python3 -m pip install --no-cache-dir -U /tmp/nubus_provisioning_listener-*.whl \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*
