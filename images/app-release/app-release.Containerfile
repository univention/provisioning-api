FROM docker-registry.knut.univention.de/knut/univention-appcenter-control:latest
RUN apt-get update && apt-get install -y jq curl gettext tree python3-pip || echo "Packages installed."
RUN pip install jinjanator
COPY send_chat.sh /usr/bin/send_chat
COPY create_app_version.sh /usr/bin/create_app_version
COPY delete_app_version.sh /usr/bin/delete_app_version
COPY render_appcenter_files.sh /usr/bin/render_appcenter_files
COPY default_release_text.txt /var/lib/default_release_text.txt