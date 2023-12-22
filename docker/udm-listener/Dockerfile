ARG LISTENER_BASE_IMAGE_TAG=latest
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base:${LISTENER_BASE_IMAGE_TAG}

# hadolint ignore=DL3006
FROM ${LISTENER_BASE_IMAGE} as final
WORKDIR /app

COPY ./src/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/
COPY ./src ./
ENV PYTHONPATH=$PYTHONPATH:/app
