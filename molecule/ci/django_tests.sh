#!/bin/bash

source ~/tracker-alpha/bin/activate
cd /var/www/django-alpha/ || exit 1
./manage.py test --noinput --keepdb
