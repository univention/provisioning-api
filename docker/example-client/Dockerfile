# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20260903@sha256:8c6b378edf59418ef6699b4dedb3715c8899e140c8f3480efaf545cca4909fa1

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.33@sha256:77280f2f771df71f90786c314fe1bbc1e023feac652969bbf139c280babf2eb7 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.13

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
  python3.13 -V && \
  python3.13 -m site && \
  python3.13 -c 'import univention.provisioning.consumer_example.main'
