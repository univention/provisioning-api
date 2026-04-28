# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.5-build.20260417@sha256:83a3b0eef92fd907fa8ec188792e607bc2d3e3a9ad0cc21e39981b728f4c98dd

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.8@sha256:3b7b60a81d3c57ef471703e5c83fd4aaa33abcd403596fb22ab07db85ae91347 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11
    # UV_PROJECT_ENVIRONMENT=/app

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./udm-transformer/uv.lock \
     ./udm-transformer/pyproject.toml \
     /app/udm-transformer/

WORKDIR /app/udm-transformer
RUN --mount=type=cache,target=/root/.cache \
  uv venv --system-site-packages && \
  uv sync \
    --locked \
    --no-dev \
    --no-install-project && \
  uv export -o ./requirements.txt

# copy source code
COPY ./udm-transformer/src /app/udm-transformer/src

RUN uv sync --locked --no-dev --no-editable

###############################################
# Stage 3: final image
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/udm-transformer/.venv/bin:$PATH

ARG USER=udm-transformer
RUN groupadd -r ${USER} -g 1000 && \
    useradd -r -d /app -g ${USER} -N ${USER} -u 1000

COPY --from=build --chown=${USER}:${USER} /app/udm-transformer/.venv /app/udm-transformer/.venv
COPY --from=build --chown=${USER}:${USER} /app/udm-transformer/requirements.txt /app/udm-transformer/requirements.txt

USER ${USER}

CMD ["udm-transformer"]

 RUN \
   python3.11 -V && \
   python3.11 -m site && \
   python3.11 -c 'import univention.provisioning.udm_transformer.main'
