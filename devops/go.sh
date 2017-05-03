#!/bin/bash
#
#

if [ ! -d devops/.venv ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

cd devops
pip install -U -r requirements.txt

# Install external ansible role dependencies
ansible-galaxy install -r requirements.yml

molecule create --driver docker
molecule converge --driver docker
