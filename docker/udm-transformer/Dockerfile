# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

###############################################
# Stage 1: build dependencies and software
FROM debian:bookworm-slim AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.9.1-python3.11-bookworm-slim@sha256:bda40d0b4bab80ba4f41dda73cd3ef2f07c9a24b0f9709372fcfbb9683ab5a3c /usr/local/bin/uv /usr/local/bin/uv
COPY --from=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python:5.2.2-build.20250828@sha256:2523fd15d25ab590918309b538510b7bd26b92ba8bed89587381ac8c3c62d324 /etc/apt/trusted.gpg.d/univention-archive-key-ucs-52x.gpg /etc/apt/trusted.gpg.d/univention-archive-key-ucs-52x.gpg

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11
    # UV_PROJECT_ENVIRONMENT=/app

RUN echo "deb http://updates.software-univention.de ucs522 main" > /etc/apt/sources.list.d/ucs.list \
    && echo "deb http://updates.software-univention.de/ errata522 main" > /etc/apt/sources.list.d/ucs-errata.list \
    && apt-get update \
    && apt-get --assume-yes --verbose-versions --no-install-recommends install python3-univention-directory-manager-rest \
    && rm -fr /var/lib/apt/lists/* /var/cache/apt/archives/*

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./udm-transformer/uv.lock \
     ./udm-transformer/pyproject.toml \
     /app/udm-transformer/

WORKDIR /app/udm-transformer
RUN --mount=type=cache,target=/root/.cache \
  uv export -o ./requirements.txt

# copy source code
COPY ./udm-transformer/src /app/udm-transformer/src

RUN --mount=type=cache,target=/root/.cache \
  uv pip install --system --break-system-packages . \
  && rm -f /usr/local/bin/uv

CMD ["/usr/local/bin/udm-transformer"]
