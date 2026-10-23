# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python
ARG UCS_BASE_IMAGE_TAG=5.3.0-build.20261022@sha256:ea444eeecf1681d2ca6e599a08779b3e078a29311f74678b2a3245474c564f61
ARG UCS_DISTROLESS_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-distroless-python
ARG UCS_DISTROLESS_IMAGE_TAG=5.3.0-build.20261022@sha256:f65cefc852c76dfd42ad0c1ad0f6885357e62899f51aa421b6f89eef550b97cf

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.13.5@sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff /uv /usr/local/bin/uv

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
#
# Distroless: no shell, so every instruction here is exec form. The user,
# os-release and CA bundle come from the base image.
FROM ${UCS_DISTROLESS_IMAGE}:${UCS_DISTROLESS_IMAGE_TAG} AS final

ENV PYTHONUNBUFFERED=1 \
    PATH=/app/consumer_example/.venv/bin:$PATH

COPY --from=build /app/consumer_example /app/consumer_example

WORKDIR /app

# Verify the entrypoint imports in the image that ships.
RUN ["python3.13", "-c", "import univention.provisioning.consumer_example.main"]

# The base image sets an ENTRYPOINT of its own; reset it so that CMD is the
# whole command line.
ENTRYPOINT []
CMD ["consumer_example"]
