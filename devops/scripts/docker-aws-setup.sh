#!/bin/bash
#
#

# Create docker remote host
sandbox_name="aws-sandbox-${USER}"
docker-machine create --driver amazonec2 $sandbox_name

# some helpful post output
echo "Now proceed to run:"
echo eval \$\(docker-machine env $sandbox_name\)
