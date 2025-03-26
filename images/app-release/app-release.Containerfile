FROM docker-registry.knut.univention.de/knut/univention-appcenter-control:latest
RUN apt-get update && apt-get install -y jq crudini curl gettext tree || echo "Packages installed."
COPY send_chat.sh /usr/bin/send_chat
COPY create_app_version.sh /usr/bin/create_app_version
COPY delete_app_version.sh /usr/bin/delete_app_version
COPY default_release_text.txt /var/lib/default_release_text.txt