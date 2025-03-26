#!/usr/bin/env bash
set -e
if [[ -z "$APP_ID" ]]; then
    echo "No APP_ID was set for this job. Aborting."
    exit 1
fi

if [[ -z "$APP_UCS_VERSION" ]]; then
    echo "No APP_UCS_VERSION was set for this job. Aborting."
    exit 1
fi


if univention-appcenter-control status "$APP_UCS_VERSION/$APP_ID" | grep -F "$APP_VERSION"; then
    echo "Removing $APP_UCS_VERSION/$APP_ID=$APP_VERSION from test appcenter."
    univention-appcenter-control remove-version --noninteractive "$APP_UCS_VERSION/$APP_ID=$APP_VERSION"
else
    echo "App version $APP_UCS_VERSION/$APP_ID=$APP_VERSION could not be found in test appcenter. Skip removal."
fi
