# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE_TAG=0.14.0-build-2024-12-12
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-520

##############################################################
# Optimized for fast rebuilds (when only tests/* is changed) #
##############################################################

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS dep_builder

ARG WORKDIR="/app"
ENV POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WEB_CONCURRENCY=1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR ${WORKDIR}

RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip=23.* \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/* \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir poetry==1.8.3 poetry-plugin-export==1.8.0 \
    && poetry config virtualenvs.create false \
    && poetry config warnings.export false

# copy dependencies source code
COPY ./CHANGELOG.md ${WORKDIR}
COPY ./backends ${WORKDIR}/backends/
COPY ./common ${WORKDIR}/common/
COPY ./consumer ${WORKDIR}/consumer/
COPY ./consumer_example ${WORKDIR}/consumer_example/
COPY ./dispatcher ${WORKDIR}/dispatcher/
COPY ./prefill ${WORKDIR}/prefill/
COPY ./rest-api ${WORKDIR}/rest-api/
COPY ./udm-transformer ${WORKDIR}/udm-transformer/

# set package version, build wheels of projects, and export dev dependencies
# Py37 packages first, so we'll update the depenedencies with the later (py311) packages.
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' ${WORKDIR}/CHANGELOG.md | tr -d '#[] ')" \
    && for DIR in common backends consumer consumer_example dispatcher prefill rest-api udm-transformer; do \
         echo "== ${WORKDIR}/${DIR} ==" \
         && poetry version "$VERSION" -C "${WORKDIR}/$DIR" \
         && python3 -m pip install --break-system-packages --no-cache-dir -U --editable ${WORKDIR}/$DIR/ \
         && if grep -q tool.poetry.group.dev.dependencies ${WORKDIR}/$DIR/pyproject.toml; then \
             poetry export --with=dev -C ${WORKDIR}/$DIR -o ${WORKDIR}/$DIR/requirements1.txt; \
             grep -v 'file:///app' ${WORKDIR}/$DIR/requirements1.txt > ${WORKDIR}/$DIR/requirements2.txt; \
             python3 -m pip install --break-system-packages --no-cache-dir -r ${WORKDIR}/$DIR/requirements2.txt; \
           fi || exit 1; \
       done \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

# install only the dependencies of the integration and e2e test
COPY ./tests/poetry.lock ./tests/pyproject.toml ./tests/README.md ${WORKDIR}/tests/
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' ${WORKDIR}/CHANGELOG.md | tr -d '#[] ')" \
    && DIR=tests \
    && echo "== ${WORKDIR}/${DIR} ==" \
    && poetry version "$VERSION" -C "${WORKDIR}/$DIR" \
    && poetry export --with=e2e-tests --with=integration-tests -C "${WORKDIR}/$DIR" -o "${WORKDIR}/$DIR/requirements1.txt" \
    && grep -v 'file:///app' "${WORKDIR}/$DIR/requirements1.txt" > "${WORKDIR}/$DIR/requirements2.txt" \
    && python3 -m pip install --break-system-packages --no-cache-dir -U -r "${WORKDIR}/$DIR/requirements2.txt"

# Reinstall py311 packages to upgrade dependencies (we got the py37 versions, because we installed 'tests' last).
# We cannot do it in one call "-r .. -r .. -r .." because there will be conflicting versions when 'poetry update' was
# not run in all projects (e.g., coverage==7.6.3 and coverage==7.6.4).
RUN for DIR in consumer dispatcher prefill rest-api udm-transformer; do \
      echo "== deps: ${DIR} ==" \
      && python3 -m pip install --break-system-packages --no-cache-dir -U -r "${WORKDIR}/${DIR}/requirements2.txt" || exit 1; \
    done


# copy and install integration and e2e tests
COPY ./tests ${WORKDIR}/tests/
RUN python3 -m pip install --break-system-packages --no-cache-dir -U --editable "${WORKDIR}/tests/"
