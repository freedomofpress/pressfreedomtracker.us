#!/bin/sh
#
# Start installing node dependencies

set -x

pnpm install --store-dir /pnpm-store && \
    pnpm run start
