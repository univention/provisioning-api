# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.5-build.20260417@sha256:83a3b0eef92fd907fa8ec188792e607bc2d3e3a9ad0cc21e39981b728f4c98dd

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.7@sha256:240fb85ab0f263ef12f492d8476aa3a2e4e1e333f7d67fbdd923d00a506a516a /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11

COPY ./common /app/common
COPY ./consumer /app/consumer
COPY ./consumer_example/uv.lock \
     ./consumer_example/pyproject.toml \
     /app/consumer_example/

WORKDIR /app/consumer_example
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./consumer_example/src /app/consumer_example/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable

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
  python3.11 -V && \
  python3.11 -m site && \
  python3.11 -c 'import univention.provisioning.consumer_example.main'
