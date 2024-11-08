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
WORKDIR ${WORKDIR}

RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-pip=23.* \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false

# copy source code
COPY ./CHANGELOG.md /tmp/
COPY ./common ${WORKDIR}/common/
COPY ./consumer ${WORKDIR}/consumer/
COPY ./consumer_example ${WORKDIR}/consumer_example/

# build wheels of dependencies and project
RUN VERSION="$(grep -o -m1 -E '^## \[.+\]' /tmp/CHANGELOG.md | tr -d '#[] ')" \
    && poetry version "$VERSION" -C ${WORKDIR}/common \
    && poetry version "$VERSION" -C ${WORKDIR}/consumer \
    && poetry version "$VERSION" -C ${WORKDIR}/consumer_example \
    && poetry build --format=wheel -C ${WORKDIR}/common \
    && poetry build --format=wheel -C ${WORKDIR}/consumer \
    && poetry build --format=wheel -C ${WORKDIR}/consumer_example

###############################################
# Stage 2: install dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG}

ARG USER=consumer_example
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

# allow image scanners like trivy to detect Python packages (additionally "pip freeze" below)
COPY ./consumer/poetry.lock ./consumer/pyproject.toml ${WORKDIR}/consumer/
COPY ./consumer_example/poetry.lock ./consumer_example/pyproject.toml ${WORKDIR}/consumer_example/

# install dependencies and project
COPY --from=dep_builder ${WORKDIR}/*/dist/*.whl /tmp
RUN useradd -m "$USER" \
    && chown "$USER":"$USER" "$WORKDIR" \
    && python3 -m pip install --break-system-packages --no-cache-dir -U pip==24.2 \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_common-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_consumer-*.whl \
    && python3 -m pip install --break-system-packages --no-cache-dir -U /tmp/nubus_provisioning_consumer_example-*.whl \
    && python3 -m pip freeze --all > ${WORKDIR}/requirements.txt \
    && rm -fr /root/.cache /root/.config /root/.local /root/* /tmp/*

ENTRYPOINT ["python3", "-m", "univention.provisioning.consumer_example.main"]
