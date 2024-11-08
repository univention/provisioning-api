# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.13.1-post-main-build-2024-09-09
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS dep_builder

ARG WORKDIR="/app"
ENV POETRY_NO_INTERACTION=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR ${WORKDIR}

RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip=23.* \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir poetry==1.8.3 poetry-plugin-export==1.8.0 \
    && poetry config virtualenvs.create false \
    && poetry config warnings.export false

# copy source code
COPY ./CHANGELOG.md /tmp/
COPY ./backends ${WORKDIR}/backends/
COPY ./common ${WORKDIR}/common/
COPY ./dispatcher ${WORKDIR}/dispatcher/

# build wheels of dependencies and project
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' /tmp/CHANGELOG.md | tr -d '#[] ')" \
    && poetry version "$VERSION" -C ${WORKDIR}/common \
    && poetry version "$VERSION" -C ${WORKDIR}/backends \
    && poetry version "$VERSION" -C ${WORKDIR}/dispatcher \
    && poetry build --format=wheel -C ${WORKDIR}/common \
    && poetry build --format=wheel -C ${WORKDIR}/backends \
    && poetry build --format=wheel -C ${WORKDIR}/dispatcher

# export dev requirements
RUN poetry export --only=dev -C ${WORKDIR}/dispatcher -o ${WORKDIR}/requirements_dispatcher_dev.txt

###############################################
# Stage 2: install dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS app_builder

ARG USER=dispatcher
ARG WORKDIR="/app"
ENV WEB_CONCURRENCY=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR ${WORKDIR}

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
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

###############################################
# Stage 3: test image
FROM app_builder AS test
WORKDIR ${WORKDIR}

COPY --from=dep_builder ${WORKDIR}/requirements_dispatcher_dev.txt /tmp

RUN grep -v 'file:///app' "/tmp/requirements_dispatcher_dev.txt" > "/tmp/requirements_dispatcher_dev2.txt" \
    && python3 -m pip install --break-system-packages --no-cache-dir -r /tmp/requirements_dispatcher_dev2.txt \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

###############################################
# Stage 3: final image
FROM app_builder AS final

ENTRYPOINT ["python3", "-m", "univention.provisioning.dispatcher.main"]
