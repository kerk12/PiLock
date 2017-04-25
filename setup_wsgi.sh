#!/usr/bin/env bash

cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf

sudo -u www-data python manage.py migrate
sudo -u www-data python manage.py createsuperuser
chown www-data:www-data db.sqlite3
chmod 700 db.sqlite3

a2ensite pilock
service apache2 restart

usermod -a -G dialout www-data

echo 'Restarting the system'
reboot