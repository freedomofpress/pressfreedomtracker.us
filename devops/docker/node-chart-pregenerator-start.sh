#!/bin/sh

set -x

if [ "${DEPLOY_ENV}" == "dev" ]; then
    npm install && npm run dev
else
    npm run start
fi
