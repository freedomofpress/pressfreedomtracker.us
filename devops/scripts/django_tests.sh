#!/bin/bash

source ~/pressfreedom/bin/activate
cd /var/www/django/
./manage.py test --noinput --keepdb
