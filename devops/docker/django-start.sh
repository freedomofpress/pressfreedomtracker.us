#!/bin/bash
# Container entrypoint script for Django applications.
set -e

django_start() {
    ./manage.py migrate
    if [ "${DJANGO_COLLECT_STATIC}" == "yes" ]; then
        ./manage.py collectstatic -c --noinput
    fi
    if [ "${DJANGO_CREATEDEVDATA:-no}" == "yes" ]; then
        ./manage.py createdevdata
    fi
    if [ "${DEPLOY_ENV}" == "dev" ]; then
        ./devops/scripts/version-file.sh
        exec ./manage.py runserver 0.0.0.0:8000
    else
        gunicorn -c /etc/gunicorn/gunicorn.py "${DJANGO_APP_NAME}.wsgi"
    fi
}

django_start
