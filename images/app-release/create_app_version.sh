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

if [[ -n "$CI_COMMIT_TAG" ]]; then
    APP_VERSION="${CI_COMMIT_TAG#"$RELEASE_TAG_PREFIX"}"
elif [[ "$CI_COMMIT_REF_NAME" == "$CI_DEFAULT_BRANCH" ]]; then
    APP_VERSION="$APP_STAGING_VERSION"
elif [[ -n "$CI_MERGE_REQUEST_ID" ]] && [[ -n "$CI_MERGE_REQUEST_IID" ]]; then
    APP_VERSION="0.0.0-MR-$CI_MERGE_REQUEST_ID-$CI_MERGE_REQUEST_PROJECT_PATH!$CI_MERGE_REQUEST_IID"
else
    echo "Could not determine app version"
    exit 1
fi

if univention-appcenter-control status --noninteractive "$APP_UCS_VERSION/$APP_ID" | grep -F "$APP_VERSION"; then
    echo "App version $APP_UCS_VERSION/$APP_ID=$APP_VERSION already exists. Skip creating app."
else
    echo "Creating $APP_UCS_VERSION/$APP_ID=$APP_VERSION in test appcenter."
    univention-appcenter-control new-version --noninteractive "$APP_UCS_VERSION/$APP_ID=$APP_STAGING_VERSION" "$APP_UCS_VERSION/$APP_ID=$APP_VERSION"
fi
univention-appcenter-control get --noninteractive --json "$APP_UCS_VERSION/$APP_ID" > appinfo.json
APP_COMPONENT_ID=$(jq --arg version "$APP_VERSION" -r '.versions[] | select(.version == $version) | .component_id' < appinfo.json)
APP_NAME=$(jq --arg version "$APP_VERSION" -r '.versions[] | select(.version == $version) | .name' < appinfo.json)
{
    echo "APP_ID=$APP_ID"
    echo "APP_COMPONENT_ID=$APP_COMPONENT_ID"
    echo "APP_UCS_VERSION=$APP_UCS_VERSION"
    echo "APP_NAME=$APP_NAME"
    echo "APP_VERSION=$APP_VERSION"
    echo "ENVIRONMENT_NAME"="$ENVIRONMENT_NAME"
} > deploy.env
jq --arg version "$APP_VERSION" '.versions[] | select(.version == $version)' < appinfo.json
