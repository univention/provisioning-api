#!/usr/bin/env bash
set -e
for appcenter_file_template in "$APPCENTER_FILE_DIR"/*.jinja; do
  DESTINATION="$APPCENTER_FILE_DIR/$(basename "$appcenter_file_template" ".jinja")"
  echo "Rendering $appcenter_file_template: "
  cat "$appcenter_file_template"
  jinjanate --filters /var/lib/jinja_source_file.py --quiet "$appcenter_file_template" --output-file "$DESTINATION"
  echo "Render result: "
  cat "$DESTINATION"
done
