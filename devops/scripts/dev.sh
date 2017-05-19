#!/bin/bash
#
#

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

pip install -U -r devops/requirements.txt

./devops/localdev/docker-config.yml
