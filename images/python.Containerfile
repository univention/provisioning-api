ARG DOCKER_PROXY
FROM ${DOCKER_PROXY}python:3.13-bookworm

RUN pip install requests python-debian pyyaml
