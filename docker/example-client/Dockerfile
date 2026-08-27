# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260825@sha256:f4b3ef96d03c574c5c3f57d4d41945a911ef05d63ca50718989b593c5d9cb6be

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13 \
    UV_PROJECT_ENVIRONMENT=/app/consumer_example/.venv

# uv needs every workspace member's manifest to load the workspace, including
# members this image does not install.
COPY ./pyproject.toml ./uv.lock /app/
COPY ./backends/pyproject.toml /app/backends/
COPY ./common/pyproject.toml /app/common/
COPY ./consumer/pyproject.toml /app/consumer/
COPY ./consumer_example/pyproject.toml /app/consumer_example/
COPY ./dispatcher/pyproject.toml /app/dispatcher/
COPY ./prefill/pyproject.toml /app/prefill/
COPY ./rest-api/pyproject.toml /app/rest-api/
COPY ./udm-transformer/pyproject.toml /app/udm-transformer/

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --package nubus-provisioning-consumer-example \
    --no-install-workspace && \
  uv export --no-dev --frozen --no-emit-workspace --no-hashes \
    --package nubus-provisioning-consumer-example -o /app/consumer_example/requirements.txt

# copy source code
COPY ./common/src /app/common/src
COPY ./consumer/src /app/consumer/src
COPY ./consumer_example/src /app/consumer_example/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --package nubus-provisioning-consumer-example --no-editable

###############################################
# Stage 2: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/consumer_example/.venv/bin:$PATH

ARG USER=consumer_example
RUN rm -fv /usr/lib/python*/EXTERNALLY-MANAGED && \
    rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/* && \
    groupadd -r ${USER} -g 1000 && \
    useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/consumer_example /app/consumer_example

USER ${USER}

CMD ["consumer_example"]

RUN \
  python3.13 -V && \
  python3.13 -m site && \
  python3.13 -c 'import univention.provisioning.consumer_example.main'
