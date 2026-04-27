ARG UCSVERSION
FROM gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-flex-${UCSVERSION}:latest
RUN apt-get update && apt-get install -y build-essential git || echo "Packages installed."
COPY build_debian_packages.sh /usr/bin/build_debian_packages

ADD --checksum=sha256:8dbc2ec159dbb6b75922ef4553b9ff56d6cd84a2f4124c75180096311dc52192 \
  https://github.com/nojima/httpie-go/releases/download/v0.7.0/httpie-go_linux_amd64 /usr/local/bin/ht
RUN chmod +x /usr/local/bin/ht

COPY scripts/ /usr/local/bin/


