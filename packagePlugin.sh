#!/bin/bash

#   creates a zip archive suitable for upload to plugins.qgis.org 
#   the plugin is assumed to be in the same directory as this script, 
#   the resulting zip is saved to the current working directory.

pluginDir="$(realpath "$(dirname ${0})")"
outputDir="$(pwd)"

if [[ -f "${pluginDir}/metadata.txt" ]]; then
	pluginVersion="$(grep -oP '(?<=version=).*$' <"${pluginDir}/metadata.txt")"
	pluginName="$(grep -oP '(?<=name=).*$' <"${pluginDir}/metadata.txt")"
fi

if [[ -z "${pluginVersion}" ]] || [[ -z "${pluginName}" ]]; then
	echo "Could not find plugin in script directory" >&2
	exit 1
fi

cd "${pluginDir}"/..

zip \
	-9 \
	-x '*.DS_Store.*' '*.git*' '*.gitignore' '*.pyc' '*.swp' '*~' "$(basename "$0")" \
	-r \
	"${outputDir}/${pluginName}-${pluginVersion}.zip" \
 	"$(basename "${pluginDir}")"


