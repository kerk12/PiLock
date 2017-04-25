#!/usr/bin/env bash

cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf

python manage.py migrate
a2ensite pilock