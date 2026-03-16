ARG DOCKER_PROXY
FROM ${DOCKER_PROXY}python:3.7-slim-bullseye AS python3.7
FROM ghcr.io/astral-sh/uv:python3.14-trixie

# python3.7 is not available through uv, but we need it for UCS 5.0
# For a list of python version in uv, see `uv python list --managed-python`
COPY --from=python3.7 /usr/local/bin/python3.7* /usr/local/bin/
COPY --from=python3.7 /usr/local/lib/python3.7 /usr/local/lib/python3.7
COPY --from=python3.7 /usr/local/lib/libpython3.7* /usr/local/lib/

RUN uv python install 3.8
RUN uv python install 3.9
RUN uv python install 3.10
RUN uv python install 3.11
RUN uv python install 3.12
RUN uv python install 3.13
