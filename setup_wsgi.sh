#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
	echo "Script must be run as root"
	exit 1
fi

echo 'Switching to /var/www'
cd /var/www/PiLock

echo 'Copying the main PiLock configuration file for Apache...'
sleep 1s
cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf

echo 'Performing DB Migration...'
sudo -u www-data python manage.py migrate

echo 'Answer yes to the following, this is needed in order to collect all the image,js and CSS files for the server to function properly.'
sleep 5s
sudo -u www-data python manage.py collectstatic

echo 'You will now be asked to create a superuser for your server. This is the default user used when managing the server with the admin interface.'
sleep 5s
sudo -u www-data python manage.py createsuperuser
chown www-data:www-data db.sqlite3
chmod 700 db.sqlite3

echo 'Enabling the main PiLock Apache configuration file...'
a2ensite pilock
echo 'Restarting Apache'
service apache2 restart

echo 'Adding the www-data user to the dialout group (needed for the Serial Port to function)...'
usermod -a -G dialout www-data

echo 'Adding cron entry to the crontab.'
(crontab -l ; echo '*/5 * * * * python /var/www/PiLock/manage.py runcrons') | crontab -

echo 'Restarting the system in 5 seconds...'
sleep 5s
reboot