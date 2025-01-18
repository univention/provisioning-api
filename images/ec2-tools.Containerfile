FROM gitregistry.knut.univention.de/univention/dist/ucs-ec2-tools:latest
RUN apt-get update && apt-get install -y rsync git colorized-logs || echo "Packages installed."
