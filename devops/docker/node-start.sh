#!/bin/sh
#
# Start installing node dependencies and leave downstream containers
# a file to poll when we are ready to go

set -x

npm install && \
    touch .node_complete && \
    npm run start
