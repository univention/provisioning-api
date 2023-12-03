ARG LISTENER_BASE_IMAGE_TAG=v0.4.1
ARG LISTENER_BASE_IMAGE=gitregistry.knut.univention.de/univention/customers/dataport/upx/container-listener-base/listener-base:${LISTENER_BASE_IMAGE_TAG}

# hadolint ignore=DL3006
FROM ${LISTENER_BASE_IMAGE} as final
WORKDIR /app

COPY ./src/udm_messaging/listener/*.py /usr/lib/univention-directory-listener/system/
COPY ./docker/udm-listener/udm-listener-entrypoint.sh /entrypoint.d/75-udm-listener-entrypoint.sh

CMD ["/command.sh"]
