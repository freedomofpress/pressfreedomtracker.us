#!/bin/bash
#
#

set -e

curdir="$(dirname $(realpath "$0") )"
source .docker_versions

# Ensure virtualenv activated and ansible roles installed
"${curdir}/env-startup"
source "${curdir}/../.venv/bin/activate"

# Ensure we are in the devops directory
cd "$(dirname $(dirname $(realpath $0) )../)"|| exit

if [ "$1" != "only_tests" ]; then
    echo "##### Pull Docker Image"
    docker pull "${CIWWW_IMAGE}@sha256:${CIWWW_VER}" &> /dev/null
    # molecule needs a tag to import
    docker tag "${CIWWW_IMAGE}@sha256:${CIWWW_VER}" "${CIWWW_IMAGE}:latest"
    echo "##### Run Django provision"
    molecule create
    molecule converge
fi

echo "##### Run Testinfra pieces"
testinfra --connection=docker --hosts=prod tests/
