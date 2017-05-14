#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
	echo "Script must be run as root"
	exit 1
fi

cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf

echo 'You will now be asked to create a superuser for your server. This is the default user used when managing the server with the admin interface.'
sleep 5s

sudo -u www-data python manage.py migrate
sudo -u www-data python manage.py createsuperuser
chown www-data:www-data db.sqlite3
chmod 700 db.sqlite3

a2ensite pilock
service apache2 restart

usermod -a -G dialout www-data

echo 'Restarting the system'
reboot