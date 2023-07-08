#!/bin/sh
#
# Start installing node dependencies and leave downstream containers
# a file to poll when we are ready to go

set -x

cd chart_pregenerator
pwd
pwd
pwd
pwd

npm install && \
    touch .node_complete && \
    npm run build && \
    npm run start
