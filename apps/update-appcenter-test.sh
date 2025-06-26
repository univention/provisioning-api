#!/bin/bash
#
# Also see https://docs.software-univention.de/app-center/5.0/en/configurations.html#installation-scripts
#

set -e

UCS_VERSION="5.2"
APP_ID="${1:-provisioning-stack}"
VERSION="$(sed -n 's/^Version\s*=\s*//p' $APP_ID/ini)"
APP_VERSION="${UCS_VERSION}/${APP_ID}=${VERSION}"
FILES_TO_COPY="$(ls $APP_ID/*)"
FILES_TO_COPY=(${FILES_TO_COPY})

selfservice () {
	local uri="https://provider-portal.software-univention.de/appcenter-selfservice/univention-appcenter-control"
	local first=$1
	shift

	USERNAME="$USER"
	[ -e "$HOME/.univention-appcenter-user" ] && USERNAME="$(< "$HOME"/.univention-appcenter-user)"

	PWDFILE="$HOME/.selfservicepwd"
	[ -e "$HOME/.univention-appcenter-pwd" ] && PWDFILE="$HOME/.univention-appcenter-pwd"

	curl -sSfL "$uri" | python3 - "$first" --username="${USERNAME}" --pwdfile="${PWDFILE}" "$@"
}

die () {
	echo "$@"
	exit 0
}

usage () {
	echo "${0##*/} [options]"
	echo ""
	echo "copy keycloak app files to test appcenter or to local cache (latest keycloak version)"
	echo ""
	echo "Options:"
	echo "  -h, --help      show this help message and exit"
	echo "  -l, --local    copy files to local cache (latest keycloak version)"
	echo "  -d, --dryn-run  dry-run, just print don't copy"
	echo "  -n, --new-version  upload new version"
}

create_new_version () {
	echo "Creating new version"
	echo "selfservice new-version $UCS_VERSION/$APP_ID $APP_VERSION"
	if ! "$dry_run"; then
		selfservice new-version $UCS_VERSION/$APP_ID $APP_VERSION
	fi
}

[ "$IGN_GIT" != "true" ] && test -n "$(git status -s)" && die "Changes in repo, do not upload app! (to override: IGN_GIT=true)"

# read arguments
opts=$(getopt \
	--longoptions "help,dry-run,new-version" \
	--name "$(basename "$0")" \
	--options "hdn" \
	-- "$@"
) || die "see -h|--help"
eval set -- "$opts"
dry_run=false
while true
do
	case "$1" in
		-h|--help)
			usage
			exit 0
			;;
		-d|--dry-run)
			dry_run=true
			shift
			;;
		-n|--new-version)
			create_new_version
			shift
			;;
		--)
			shift
			break
			;;
	esac
done

### The order of the arguments doesn't matter, the univention-appcenter-control script recongnizes the filenames and file extensions.
echo "selfservice upload $APP_VERSION ${FILES_TO_COPY[*]}"
if ! "$dry_run"; then
	selfservice upload "$APP_VERSION" "${FILES_TO_COPY[@]}"
fi
