ARG DOCKER_PROXY=
ARG PYTHON_IMAGE=python:3.12-bookworm
ARG BASEDPYRIGHT_VERSION=1.39.3
ARG UV_VERSION=0.11.9
FROM ${DOCKER_PROXY}${PYTHON_IMAGE}

ARG BASEDPYRIGHT_VERSION UV_VERSION
# Match pre-commit docker_image language which mounts the repo at /src and sets --workdir /src.
# Keeps working-directory consistent between prek/pre-commit invocations and local baseline generation.
WORKDIR /src
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PIP_NO_CACHE_DIR=1 \
	PYTHONDONTWRITEBYTECODE=1
# Keep the image focused on a pinned basedpyright CLI.
# Retain uv only for workspace-local dependency setup workflows such as `uv sync --dev`.
RUN pip install --no-cache-dir \
	"uv==${UV_VERSION}" \
	&& uv pip install --system "basedpyright==${BASEDPYRIGHT_VERSION}" \
	&& basedpyright --version
