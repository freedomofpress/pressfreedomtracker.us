#!/bin/sh
#
# Start installing node dependencies

set -x

# The stats file is gitignored, so a stale one survives branch switches and
# satisfies the healthcheck before webpack has rebuilt anything. Django starts
# on that signal, then webpack's `clean` deletes the file out from under it.
rm -f build/static/bundles/webpack-stats.json

pnpm install --store-dir /pnpm-store && \
    pnpm run start
