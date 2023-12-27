ARG LISTENER_BASE_IMAGE_TAG=v0.4.1
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base:${LISTENER_BASE_IMAGE_TAG}
ARG PYTHON_VERSION=3.7
ARG WORKDIR="/app"

# hadolint ignore=DL3006
FROM library/python:${PYTHON_VERSION}-slim as builder
ARG WORKDIR
WORKDIR ${WORKDIR}

ENV \
    PATH="/home/${USER}/.local/bin:${PATH}" \
    PYTHONPATH="." \
    WEB_CONCURRENCY=1 \
    # Do not buffer `stdout`
    PYTHONUNBUFFERED=1 \
    # Do not create `.pyc` files
    PYTHONDONTWRITEBYTECODE=1 \
    # Do not ask questions
    POETRY_NO_INTERACTION=1 \
    # Put .venv inside source folder
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    # Cache of poetry
    POETRY_CACHE_DIR=/tmp/poetry_cache

# copy source code
COPY ./src ${WORKDIR}/src
COPY logging.yaml \
     poetry.lock \
     pyproject.toml \
     README.md \
     ${WORKDIR}/

RUN \
    # install Poetry
    pip install --no-cache-dir poetry==1.5.1 && \
    # install dependencies \
    poetry config installer.max-workers 10 && \
    poetry install --only main --no-ansi -vvv

############################################### \

from builder as test

RUN poetry install --with dev

FROM ${LISTENER_BASE_IMAGE} as final
ARG WORKDIR
ARG PYTHON_VERSION

WORKDIR ${WORKDIR}
COPY --from=builder ${WORKDIR} ${WORKDIR}

COPY ./src/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/
COPY ./docker/udm-listener/rest /usr/lib/python3/dist-packages/univention/admin/rest
COPY ./docker/udm-listener/management /usr/lib/python3/dist-packages/univention/management

ENV PYTHONPATH=$PYTHONPATH:${WORKDIR}/src:${WORKDIR}/.venv/lib/python${PYTHON_VERSION}/site-packages