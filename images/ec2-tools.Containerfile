FROM gitregistry.knut.univention.de/univention/infrastructure/ucs-ec2-tools:latest
RUN apt-get update && apt-get install -y rsync git colorized-logs curl crudini || echo "Packages installed."
