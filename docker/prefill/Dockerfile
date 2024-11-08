# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.14.0-build-2024-12-12
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
COPY ./prefill ${WORKDIR}/prefill/

# build wheels of dependencies and project
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' /tmp/CHANGELOG.md | tr -d '#[] ')" \
    && poetry version "$VERSION" -C ${WORKDIR}/common \
    && poetry version "$VERSION" -C ${WORKDIR}/backends \
    && poetry version "$VERSION" -C ${WORKDIR}/prefill \
    && poetry build --format=wheel -C ${WORKDIR}/common \
    && poetry build --format=wheel -C ${WORKDIR}/backends \
    && poetry build --format=wheel -C ${WORKDIR}/prefill

# export dev requirements
RUN poetry export --only=dev -C ${WORKDIR}/prefill -o ${WORKDIR}/requirements_prefill_dev.txt

###############################################
# Stage 2: install dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS app_builder

ARG USER=prefill
ARG WORKDIR="/app"
ENV WEB_CONCURRENCY=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR ${WORKDIR}

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip \
      python3-univention-directory-manager-rest-client \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

# install dependencies and project
COPY --from=dep_builder ${WORKDIR}/*/dist/*.whl /tmp
RUN useradd -m "$USER" \
    && chown "$USER":"$USER" "$WORKDIR" \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_common-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_backends-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_prefill-*.whl \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

###############################################
# Stage 3: test image
FROM app_builder AS test
WORKDIR ${WORKDIR}

COPY --from=dep_builder ${WORKDIR}/requirements_prefill_dev.txt /tmp

RUN grep -v 'file:///app' "/tmp/requirements_prefill_dev.txt" > "/tmp/requirements_prefill_dev2.txt" \
    && python3 -m pip install --break-system-packages --no-cache-dir -r /tmp/requirements_prefill_dev2.txt \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

###############################################
# Stage 3: final image
FROM app_builder AS final

ENTRYPOINT ["python3", "-m", "univention.provisioning.prefill.main"]
