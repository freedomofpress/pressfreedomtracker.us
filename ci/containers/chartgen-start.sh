#!/bin/bash
# Container entrypoint for the dev chart pregenerator (esbuild watch + nodemon).
set -e

# exec so npm is PID 1 and receives SIGTERM directly; without it bash holds
# PID 1, swallows the signal, and `compose down` waits out the grace period.
exec npm run dev
