#!/bin/bash
#
#

if [ $# -eq 0 ]; then echo "ERR - Missing positional molecule action argument"; exit 1; fi

# Allow setting Django port to random values by env variable
if [ "${RAND_PORT-false}" != "false" ]; then
    export RAND_PORT=true
fi

if [ ! -f devops/.venv/bin/activate ]; then virtualenv --no-site-packages devops/.venv; fi
source devops/.venv/bin/activate

pip install -U -r devops/requirements.txt > /dev/null

molecule $1 -s dev
