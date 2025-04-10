ARG UCSVERSION
FROM gitregistry.knut.univention.de/univention/components/ucs-base-image/ucs-base-${UCSVERSION}:latest
RUN apt-get update && apt-get install -y build-essential git || echo "Packages installed."
COPY build_debian_packages.sh /usr/bin/build_debian_packages
