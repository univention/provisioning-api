# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.2.3-build.20251113@sha256:2d2b8ca20dfec4cb761b6e465d2b0a8e74007d8d985851ac937017e475c86af6

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.5.8@sha256:0bc959d4cc56e42cbd9aa9b63374d84481ee96c32803eea30bd7f16fd99d8d56 /uv /usr/local/bin/uv

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

RUN apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3-univention-directory-manager-rest \
    && rm -fv /usr/lib/python*/EXTERNALLY-MANAGED \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

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
