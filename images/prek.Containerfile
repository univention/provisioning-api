FROM docker-registry.knut.univention.de/knut/prek:latest
RUN apt-get update && apt-get install -y curl jq gcc python3-dev libldap2-dev libsasl2-dev || echo "Packages installed."
ENTRYPOINT []