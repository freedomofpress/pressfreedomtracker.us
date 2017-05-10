#!/bin/bash

source ~/pressfreedom/bin/activate
/var/www/django/manage.py test --noinput --keepdb
