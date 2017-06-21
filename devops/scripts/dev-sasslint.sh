#!/bin/bash
#
#
#

curdir="$(dirname "$(realpath "$0")" )"

source "$curdir/../../.docker_versions" || exit 1

docker run -it -v "${PWD}:/lintme" -w /lintme "${SASSLINT_IMAGE}@sha256:${SASSLINT_VER}"
