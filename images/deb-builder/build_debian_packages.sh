#!/usr/bin/env bash
set -e

DEBIAN_ARTIFACTS_DIRECTORY=artifacts

mkdir "$DEBIAN_ARTIFACTS_DIRECTORY"
mkdir build
for dir in $DEBIAN_SOURCE_DIRECTORIES; do
    cd "$CI_PROJECT_DIR"
    mv "$dir" build/
    cd "build/$dir"
    apt-get --quiet --assume-yes build-dep .
    dpkg-buildpackage --unsigned-source --unsigned-changes
done
cd "$CI_PROJECT_DIR"

mv build/*.deb "$DEBIAN_ARTIFACTS_DIRECTORY"
