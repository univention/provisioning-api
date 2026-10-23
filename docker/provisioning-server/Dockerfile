# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

# One image for the four Python services (api, dispatcher, prefill,
# udm-transformer). They share almost all of their dependencies, so four
# separate images multiplied the same packages across four SBOMs. Select the
# process with the container command; see docs/simplify/README.md (W2).

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20261022@sha256:ea444eeecf1681d2ca6e599a08779b3e078a29311f74678b2a3245474c564f61

ARG UCS_DISTROLESS_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-distroless-python
ARG UCS_DISTROLESS_IMAGE_TAG=5.3.0-build.20261022@sha256:f65cefc852c76dfd42ad0c1ad0f6885357e62899f51aa421b6f89eef550b97cf

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PYTHON=python3.13 \
  UV_PROJECT_ENVIRONMENT=/app/.venv

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
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    --no-install-workspace && \
  uv export --no-dev --frozen --no-emit-workspace --no-hashes \
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    -o /app/requirements.txt

# copy source code
COPY ./backends/src /app/backends/src
COPY ./common/src /app/common/src
COPY ./dispatcher/src /app/dispatcher/src
COPY ./prefill/src /app/prefill/src
COPY ./rest-api/src /app/rest-api/src
COPY ./udm-transformer/src /app/udm-transformer/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --package nubus-provisioning-rest-api \
    --package nubus-provisioning-dispatcher \
    --package nubus-provisioning-prefill \
    --package nubus-provisioning-udm-transformer \
    --no-editable

###############################################
# Stage 2: final image
#
# Distroless: no shell, so no shell-form RUN steps here. The user, os-release
# and CA bundle come from the base image.
FROM ${UCS_DISTROLESS_IMAGE}:${UCS_DISTROLESS_IMAGE_TAG} AS final

EXPOSE 7777

ENV PYTHONUNBUFFERED=1 \
  PATH=/app/.venv/bin:$PATH

COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/requirements.txt /app/requirements.txt

WORKDIR /app

# Verify every entrypoint imports in the image that ships.
# There is no /bin/sh, so SHELL is the interpreter.
# hadolint shellchecks the heredoc as sh regardless of SHELL.
SHELL ["python3.13", "-c"]
# hadolint ignore=SC2239
RUN <<EOF
import pydantic
import univention.provisioning.dispatcher.main
import univention.provisioning.prefill.main
import univention.provisioning.udm_transformer.main
try:
    import univention.provisioning.rest.main
except pydantic.ValidationError:
    pass  # main.py reads its settings at import time, after all of its imports ran
EOF

# hadolint only parses the heredoc as closed when a blank line follows EOF.
SHELL ["/bin/sh", "-c"]

# No default process: the base image's ENTRYPOINT is reset and no CMD is set,
# so every caller has to name the service it wants (see helm values / compose).
ENTRYPOINT []
