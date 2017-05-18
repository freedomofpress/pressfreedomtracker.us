#!/bin/bash
#
#

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

cd devops || exit
pip install -U -r requirements.txt

# Install external ansible role dependencies
ansible-galaxy install -r requirements.yml

docker pull msheiny/debian-jessie-systemd:latest
if [ "$1" != "only_tests" ]; then
    molecule create
    molecule converge
fi

testinfra --connection=docker --hosts=prod tests/
