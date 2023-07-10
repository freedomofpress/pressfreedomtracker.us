#!/bin/sh

set -x

cd chart_pregenerator

npm install && \
    touch .node_complete && \
    npm run build && \
    npm run start
