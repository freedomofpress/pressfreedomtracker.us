#!/bin/bash
#
#

set -e

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

cd devops || exit
echo "##### Install pip requirements"
pip install -U -r requirements.txt 1> /dev/null

# Install external ansible role dependencies
echo "##### Install ansible galaxy requirements"
ansible-galaxy install -r requirements.yml &> /dev/null

echo "##### Run sass linter"
# Start sasslinter container, have to get a little hacky since its running on a
# remote docker instance
docker run -d --entrypoint=/bin/ash --name sasslint quay.io/freedomofpress/sasslinter -c 'tail -f /dev/null'
echo "Copying git directory to remote docker container..."
docker cp "${PWD}/../" sasslint:/lintme
docker exec -it sasslint ash -c 'cd /lintme && /usr/local/bin/sass-lint'

echo "##### Run Debian playbook"
docker pull msheiny/debian-jessie-systemd:latest &> /dev/null
if [ "$1" != "only_tests" ]; then
    molecule create
    molecule converge
fi

echo "##### Run Testinfra pieces"
testinfra --connection=docker --hosts=prod tests/
