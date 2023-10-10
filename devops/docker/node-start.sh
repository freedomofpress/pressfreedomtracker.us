#!/bin/sh
#
# Start installing node dependencies

set -x

npm install && \
    npm run start
