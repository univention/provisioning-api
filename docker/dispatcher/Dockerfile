# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python-521
ARG UCS_BASE_IMAGE_TAG=0.17.3-build-2025-05-11

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS dep_builder

ARG WORKDIR="/app"
ENV POETRY_NO_INTERACTION=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip \
    && python3 -m pip install --break-system-packages --no-cache-dir poetry==1.8.3 poetry-plugin-export==1.8.0

COPY ./backends/poetry.lock \
     ./backends/pyproject.toml \
     ${WORKDIR}/backends/
WORKDIR ${WORKDIR}/backends/
RUN poetry export -C ${WORKDIR}/backends -f requirements.txt > /requirements-backend.txt

COPY ./common/poetry.lock \
     ./common/pyproject.toml \
     ${WORKDIR}/common/
WORKDIR ${WORKDIR}/common/
RUN poetry export -C ${WORKDIR}/common -f requirements.txt > /requirements-common.txt

COPY ./dispatcher/poetry.lock \
     ./dispatcher/pyproject.toml \
     ${WORKDIR}/dispatcher/
RUN poetry export -C ${WORKDIR}/dispatcher -f requirements.txt > /requirements-dispatcher.txt

# copy source code
COPY ./backends ${WORKDIR}/backends/
COPY ./common ${WORKDIR}/common/
COPY ./dispatcher ${WORKDIR}/dispatcher/

# build wheels of dependencies and project
RUN poetry build --format=wheel -C ${WORKDIR}/common \
    && poetry build --format=wheel -C ${WORKDIR}/backends \
    && poetry build --format=wheel -C ${WORKDIR}/dispatcher

# ###############################################
# Stage 2: install dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS app_builder

ARG USER=dispatcher
ARG WORKDIR="/app"
ENV WEB_CONCURRENCY=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR ${WORKDIR}

RUN apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=23.* \
    && rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

# install dependencies and project
COPY --from=dep_builder ${WORKDIR}/*/dist/*.whl /tmp
RUN useradd -m "$USER" \
    && chown "$USER":"$USER" "$WORKDIR" \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_common-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_backends-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_dispatcher-*.whl \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*


ENTRYPOINT ["python3", "-m", "univention.provisioning.dispatcher.main"]
