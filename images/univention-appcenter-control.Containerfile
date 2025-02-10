FROM docker-registry.knut.univention.de/knut/univention-appcenter-control:latest
RUN apt-get update && apt-get install -y jq crudini || echo "Packages installed."
