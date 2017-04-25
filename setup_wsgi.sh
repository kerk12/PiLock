#!/usr/bin/env bash

cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf

sudo -u www-data python manage.py migrate
a2ensite pilock
service apache2 restart