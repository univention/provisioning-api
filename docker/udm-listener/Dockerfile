# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024-2026 Univention GmbH

# Inspired by: https://hynek.me/articles/docker-uv/

ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base
ARG UCS_BASE_IMAGE_TAG=5.2.6-build.20260706@sha256:e82e71bbc6008e440a72078b459a2cef2f3a7333a4680a8bfb6448469490e2d6

###############################################
# Stage 1: build dependencies and software
FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS ucs-sources-base

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

FROM ucs-sources-base AS deb_builder

COPY docker/udm-listener/patches/*.patch /root/

WORKDIR /root/src/debian/

# hadolint ignore=DL3003
RUN \
  apt-get build-dep --assume-yes univention-directory-listener && \
  apt-get source univention-directory-listener && \
  cd univention-directory-listener-* && \
  patch -p3 < /root/0001-allow-to-specify-separate-notifier-address.patch && \
  dpkg-buildpackage -uc -us -b

FROM ucs-sources-base AS listener-base

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

# hadolint ignore=DL3008
RUN \
  echo "postfix postfix/main_mailer_type string 'Satellite system'" \
  | debconf-set-selections && \
  echo "postfix postfix/mailname string univention-directory-listener" \
  | debconf-set-selections && \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  postfix

COPY --from=deb_builder \
  /root/src/debian/univention-directory-listener_*.deb /root/

# hadolint ignore=DL3008
RUN \
  apt-get --assume-yes --verbose-versions --no-install-recommends install \
  /root/univention-directory-listener_*.deb \
  python3-distutils \
  python3-univention-directory-manager && \
  awk \
  '/^Package: univention-directory-listener$/{ while(!/^Version: /){getline} print $2 }' \
  /var/lib/dpkg/status > /version

RUN \
  rm /usr/lib/univention-directory-listener/system/*

COPY docker/udm-listener/command.sh /

CMD ["/command.sh"]

FROM listener-base AS build

SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

COPY --from=ghcr.io/astral-sh/uv:0.11.32@sha256:df4cae8f3a96d175e2e5f992e597550000edbe78fdc2594d5cd8de1a217f504c /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.11

COPY ./backends /app/backends
COPY ./common /app/common
COPY ./listener/uv.lock \
     ./listener/pyproject.toml \
     /app/listener/

WORKDIR /app/listener
RUN --mount=type=cache,target=/root/.cache \
  uv sync \
    --locked \
    --no-dev \
    --no-install-project && \
  uv export -o ./requirements.txt

COPY ./listener/src /app/listener/src

RUN --mount=type=cache,target=/root/.cache \
  uv sync --locked --no-dev --no-editable

###############################################
# Stage 2: final image
FROM listener-base AS final
SHELL ["/bin/bash", "-uxo", "pipefail", "-c"]

RUN \
  mkdir /var/secrets/ /etc/ldap && \
  echo "univention" > /var/secrets/ldap_password && \
  echo -e "URI ldap://ldap-server:389\nBASE dc=univention-organization,dc=intranet" > /etc/ldap/ldap.conf && \
  /usr/sbin/ucr set \
    server/role="memberserver" \
    ldap/master="ldap-server" \
    ldap/master/port=389 \
    ldap/hostdn="cn=admin,dc=univention-organization,dc=intranet" \
    ldap/base="dc=univention-organization,dc=intranet" \
    directory/manager/starttls=0 \
    listener/debug/level="3"

COPY ./docker/udm-listener/*.patch /tmp/
RUN apt-get update && \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
    patch && \
    patch -p1 -i /tmp/listener.py.patch /usr/lib/python3/dist-packages/listener.py && \
    patch -p1 -i /tmp/handler_logging.py.patch /usr/lib/python3/dist-packages/univention/listener/handler_logging.py && \
    apt-get purge --auto-remove --assume-yes patch && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/listener/.venv/lib/python3.11/site-packages

COPY ./listener/src/nubus-provisioning.py /usr/lib/univention-directory-listener/system/

COPY --from=build /app/listener /app/listener

USER ${USER}

