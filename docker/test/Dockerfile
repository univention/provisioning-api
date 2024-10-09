# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.13.1-post-main-build-2024-09-09
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} as dep_builder

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
COPY ./consumer ${WORKDIR}/consumer/
COPY ./consumer_example ${WORKDIR}/consumer_example/
COPY ./dispatcher ${WORKDIR}/dispatcher/
COPY ./prefill ${WORKDIR}/prefill/
COPY ./rest-api ${WORKDIR}/rest-api/
COPY ./tests ${WORKDIR}/tests/
COPY ./udm-transformer ${WORKDIR}/udm-transformer/

# set package version, build wheels of projects, and export dev dependencies
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' /tmp/CHANGELOG.md | tr -d '#[] ')" \
    && for DIR in common backends consumer consumer_example dispatcher prefill rest-api udm-transformer; do \
         echo "== ${WORKDIR}/${DIR} ==" \
         && poetry version "$VERSION" -C "${WORKDIR}/$DIR" \
         && poetry build --format=wheel -C ${WORKDIR}/$DIR \
         && if grep -q tool.poetry.group.dev.dependencies ${WORKDIR}/$DIR/pyproject.toml; then \
             poetry export --only=dev -C ${WORKDIR}/$DIR -o ${WORKDIR}/requirements_${DIR}_dev.txt; \
           fi || exit 1; \
       done \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

###############################################
# Stage 2: install dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

ARG USER=test
ARG WORKDIR="/app"
ENV WEB_CONCURRENCY=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]
WORKDIR ${WORKDIR}

# allow image scanners like trivy to detect Python packages (additionally "pip freeze" below)
COPY ./backends/poetry.lock ./backends/pyproject.toml ${WORKDIR}/backends/
COPY ./common/poetry.lock ./common/pyproject.toml ${WORKDIR}/common/
COPY ./consumer/poetry.lock ./consumer/pyproject.toml ${WORKDIR}/consumer/
COPY ./consumer_example/poetry.lock ./consumer_example/pyproject.toml ${WORKDIR}/consumer_example/
COPY ./dispatcher/poetry.lock ./dispatcher/pyproject.toml ${WORKDIR}/dispatcher/
COPY ./prefill/poetry.lock ./prefill/pyproject.toml ${WORKDIR}/prefill/
COPY ./rest-api/poetry.lock ./rest-api/pyproject.toml ${WORKDIR}/rest-api/
COPY ./udm-transformer/poetry.lock ./udm-transformer/pyproject.toml ${WORKDIR}/udm-transformer/

# copy test code
COPY ./tests ${WORKDIR}/tests/

# install dependencies and project
COPY --from=dep_builder ${WORKDIR}/*/dist/*.whl ${WORKDIR}/requirements_*_dev.txt /tmp/
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-pip=23.* \
      python3-univention-directory-manager-rest-client=12.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*
RUN python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && for DIR in common backends consumer consumer_example dispatcher prefill rest-api udm-transformer; do \
         python3 -m pip install --break-system-packages --no-cache-dir -U "/tmp/nubus_provisioning_$(echo $DIR | tr - _)-*.whl" \
         && if [ -e /tmp/requirements_${DIR}_dev.txt ]; then \
              python3 -m pip install --break-system-packages --no-cache-dir -r /tmp/requirements_${DIR}_dev.txt; \
            fi || exit 1; \
       done || exit 1 \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*
