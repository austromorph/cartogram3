#!/bin/bash

set +m -euo pipefail
IFS=$'\n\t '

declare PLUGIN_NAME
declare PLUGIN_VERSION

mkdir -p build dist src

if [[ -f "src/metadata.txt" ]]; then
	PLUGIN_NAME="$(grep -oP '(?<=name=).*$' <"src/metadata.txt")"
	PLUGIN_VERSION="$(grep -oP '(?<=version=).*$' <"src/metadata.txt")"
fi

if [[ -z "${PLUGIN_NAME}" ]] || [[ -z "${PLUGIN_VERSION}" ]]; then
	echo "Could not find plugin" >&2
	exit 1
fi

rsync \
    --archive \
    --exclude='*.DS_Store.*' \
    --exclude='*.pyc' \
    --exclude='*.swp' \
    src/ \
    build/ 

zip \
	-9 \
	-r \
	"dist/${PLUGIN_NAME}-${PLUGIN_VERSION}.zip" \
    "build/"
