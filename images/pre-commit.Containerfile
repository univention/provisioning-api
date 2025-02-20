FROM docker-registry.knut.univention.de/knut/pre-commit:latest
RUN apt-get update && apt-get install -y curl jq || echo "Packages installed."