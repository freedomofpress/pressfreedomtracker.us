#!/bin/bash
#
#
# Run ansible roles for NGINX, Node, Postgres ontop of Base CI config
# Use that image to commit and publish to repository

set -e

curdir="$(dirname $(realpath $0) )"

# Setup environment (ansible + roles)
"${curdir}/env-startup"
source "${curdir}/../.venv/bin/activate"

cd "${curdir}/../docker/django" || exit

ansible-playbook ./playbook.yml -K
docker commit -p ci-django-ansible quay.io/freedomofpress/ci-webserver

echo "When you are ready, run 'docker push quay.io/freedomofpress/ci-webserver'"
