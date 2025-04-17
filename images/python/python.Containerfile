ARG DOCKER_PROXY
FROM ${DOCKER_PROXY}python:3.13-bookworm

ADD https://provider-portal.software-univention.de/appcenter-selfservice/univention-appcenter-control /usr/bin/univention-appcenter-control
RUN mkdir /usr/local/share/ca-certificates/my-custom-ca
COPY ucs-root-ca.crt /usr/local/share/ca-certificates/my-custom-ca/ucs-root-ca.crt
RUN update-ca-certificates
RUN chmod 755 /usr/bin/univention-appcenter-control
COPY copy_app_binaries /usr/bin/copy_app_binaries
RUN pip install requests python-debian pyyaml

ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE /etc/ssl/certs/ca-certificates.crt