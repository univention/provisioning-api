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

IS_ERRATA=false
if [[ -n "$CI_COMMIT_TAG" ]]; then
    APP_VERSION="${CI_COMMIT_TAG#"$RELEASE_TAG_PREFIX"}"
    # An errata tag (e.g. release-5.2v4-errata1) is a package update into an
    # already published app version. Strip the -errataN suffix so APP_VERSION
    # points at the existing version instead of creating a new one.
    if [[ "$APP_VERSION" =~ ^(.+)-errata[0-9]+$ ]]; then
        IS_ERRATA=true
        APP_VERSION="${BASH_REMATCH[1]}"
        echo "Detected errata release: targeting existing app version $APP_VERSION."
    fi
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
elif [[ "$IS_ERRATA" == "true" ]]; then
    echo "Errata target app version $APP_UCS_VERSION/$APP_ID=$APP_VERSION does not exist."
    echo "An errata can only update an already published app version. Aborting."
    exit 1
else
    echo "Creating $APP_UCS_VERSION/$APP_ID=$APP_VERSION in test appcenter."
    univention-appcenter-control new-version --noninteractive "$APP_UCS_VERSION/$APP_ID=$APP_STAGING_VERSION" "$APP_UCS_VERSION/$APP_ID=$APP_VERSION"
fi
univention-appcenter-control get --noninteractive --json "$APP_UCS_VERSION/$APP_ID" > appinfo.json
APP_COMPONENT_ID=$(jq --arg version "$APP_VERSION" --arg ucs_version "$APP_UCS_VERSION" -r '.versions[] | select(.version == $version and .ucs_version == $ucs_version) | .component_id' < appinfo.json)
APP_NAME=$(jq --arg version "$APP_VERSION" --arg ucs_version "$APP_UCS_VERSION" -r '.versions[] | select(.version == $version and .ucs_version == $ucs_version) | .name' < appinfo.json)
{
    echo "APP_ID=$APP_ID"
    echo "APP_COMPONENT_ID=$APP_COMPONENT_ID"
    echo "APP_UCS_VERSION=$APP_UCS_VERSION"
    echo "APP_NAME=$APP_NAME"
    echo "APP_VERSION=$APP_VERSION"
    echo "IS_ERRATA=$IS_ERRATA"
    echo "ENVIRONMENT_NAME"="$ENVIRONMENT_NAME"
} > deploy.env
jq --arg version "$APP_VERSION" --arg ucs_version "$APP_UCS_VERSION" '.versions[] | select(.version == $version and .ucs_version == $ucs_version)' < appinfo.json
