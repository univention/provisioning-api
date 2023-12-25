# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

###############################################################################
# Dockerfile for the univention-directory-notifier

ARG UCS_BASE_IMAGE_TAG=latest
ARG UCS_BASE_IMAGE=gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-506

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS build

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]

WORKDIR /apt

###############################################################################
# Install univention-directory-notifier

# The following scripts get called during dpkg-install but are not required
# in a container environment
COPY fake.sh /usr/local/bin/call_joinscript
COPY fake.sh /usr/local/bin/create_logfile
COPY fake.sh /usr/local/bin/ucr
COPY fake.sh /usr/local/bin/systemctl
COPY fake.sh /usr/local/bin/univention-config-registry

RUN \
  apt-get update && \
  apt-get download \
    libunivention-debug1=12.0.* \
    python3-univention-config-registry=15.0.* \
    python3-univention-debhelper=2.0.* \
    univention-directory-notifier=14.0.* && \
  mkdir /usr/share/univention-lib/ && \
  # The original file would source many bash-helper-functions not required here.
  touch /usr/share/univention-lib/all.sh && \
  dpkg --install --force-depends /apt/* && \
  rm -rf /apt /var/lib/apt/lists/* && \
  awk \
    '/^Package: univention-directory-notifier$/{ while(!/^Version: /){getline} print $2 }' \
    /var/lib/dpkg/status > /version
RUN ["chmod", "+x", "/entrypoint.d/"]

###############################################################################
# Second stage image to get rid of unneeded files

FROM ${UCS_BASE_IMAGE}:${UCS_BASE_IMAGE_TAG} AS final

ARG LABEL_CREATED=undefined
ARG LABEL_REVISION=undefined
ARG LABEL_SOURCE=undefined
ARG LABEL_VERSION=undefined

SHELL ["/bin/bash", "-euxo", "pipefail", "-c"]
RUN \
  apt-get update && \
  DEBIAN_FRONTEND=noninteractive \
    apt-get --assume-yes --verbose-versions --no-install-recommends install \
      python3=3.* \
      python3-ldap=3.* \
      python3-lazy-object-proxy=1.* \
      python3-six=1.* \
  && \
  rm -rf /var/lib/apt/lists/*

# Copy python-univention-config-registry dependency for univention-translog
COPY --from=build \
  /usr/lib/python3/dist-packages/univention/config_registry/ \
  /usr/lib/python3/dist-packages/univention/config_registry/

COPY --from=build \
  /usr/lib/python3/dist-packages/univention/config_registry_info.py \
  /usr/lib/python3/dist-packages/univention/config_registry_info.py

COPY --from=build \
  /usr/lib/python3/dist-packages/univention/info_tools.py \
  /usr/lib/python3/dist-packages/univention/info_tools.py

# Why do we need this again?
# Copy debhelper dependency for univention-translog
COPY --from=build \
  /usr/lib/python3/dist-packages/univention/debhelper.py \
  /usr/lib/python3/dist-packages/univention/debhelper.py

# Copy dependencies for univention-directory-notifier
# libuniventiondebug.so.1.0.0 from libunivention-debug1
COPY --from=build \
  /usr/lib/x86_64-linux-gnu/libuniventiondebug.so.1.0.0 \
  /usr/lib/x86_64-linux-gnu/

# Copy translog import script
# univention-directory-notifier
COPY --from=build \
  /usr/share/univention-directory-notifier/univention-translog \
  /usr/share/univention-directory-notifier/

# Copy daemon watching /var/lib/univention-ldap/listener/listener
# univention-directory-notifier
COPY --from=build \
  /usr/sbin/univention-directory-notifier \
  /usr/sbin/univention-directory-notifier


#COPY --from=build \
#  /version \
#  /version

# TODO: remove log-dir, when log-to-stdout has been released
#   https://forge.univention.org/bugzilla/show_bug.cgi?id=52716
RUN \
  # Needed to help Python find the config_registry module in there.
  touch /usr/lib/python3/dist-packages/univention/__init__.py && \
  # Needed because the notifier creates its log-file in there.
  mkdir /var/log/univention/ && \
  SRC=$(find /usr/lib/x86_64-linux-gnu -type f -name 'libuniventiondebug.so.1.*' -printf "%f") && \
  ln --symbolic \
    "${SRC}" \
    /usr/lib/x86_64-linux-gnu/libuniventiondebug.so.1 && \
  ln --symbolic \
    /dev/stdout \
    /var/log/univention/notifier.log && \
  # univention-translog tries to create /etc/univention/base-forced.conf
  mkdir -p /etc/univention/ && \
  # univention-translong tries to open this file somewhere
  # TRANSFILE ( ALL ) : E: failed to open /var/lib/univention-ldap/schema/id
  mkdir -p /var/lib/univention-ldap-local/schema/id/ && \
  echo '1' > /var/lib/univention-ldap-local/schema/id/id

COPY entrypoint.sh /entrypoint.d/50-entrypoint.sh
COPY run-notifier.sh /
RUN ["chmod", "+x", "/run-notifier.sh"]
RUN ["chmod", "+x", "/entrypoint.d/50-entrypoint.sh"]

CMD [ \
  "/run-notifier.sh", \
  "-d 4", \
  "-v 3", \
  "-F" \
]

LABEL org.opencontainers.image.created="${LABEL_CREATED}"
LABEL org.opencontainers.image.description="Univention LDAP Notifier"
LABEL org.opencontainers.image.licenses="AGPL-3.0-or-later"
LABEL org.opencontainers.image.revision="${LABEL_REVISION}"
LABEL org.opencontainers.image.source="${LABEL_SOURCE}"
LABEL org.opencontainers.image.title="upx-ldap-notifier"
LABEL org.opencontainers.image.url="https://docs.software-univention.de/manual-5.0.html#introduction:Listener_notifier_replication"
LABEL org.opencontainers.image.vendor="Univention GmbH"
LABEL org.opencontainers.image.version="${LABEL_VERSION}"

# [EOF]
