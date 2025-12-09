FROM docker-registry.knut.univention.de/knut/prek:latest
RUN apt-get update && apt-get install -y curl jq || echo "Packages installed."
ENTRYPOINT []