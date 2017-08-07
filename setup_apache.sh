#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
	echo "Script must be run as root"
	exit 1
fi

echo 'Installing required packages'
sleep 2s
apt-get update
apt-get -y install apache2 libapache2-mod-wsgi python-pip
a2enmod wsgi

echo 'Creating the project directory in /var/www and copying files...'
sleep 2s
mkdir -p /var/www/PiLock
cp -r $(pwd) /var/www/PiLock/

echo 'Installing Python Package requirements...'
sleep 2s
pip install -r requirements.txt

echo 'Please answer these questions, so that we can create an SSL certificate. Remember that the FQDN (or common name) will be the final address that the server will be available at.'
sleep 3s
mkdir /etc/apache2/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/pilock.key -out /etc/apache2/ssl/pilock.crt
chmod -R 400 /etc/apache2/ssl
a2enmod ssl


echo -e 'A Self-Signed Certificate has been created in /etc/apache2/ssl. You now need to configure Apache to work with that certificate.'
echo -e 'For more info: \n https://hallard.me/enable-ssl-for-apache-server-in-5-minutes/'
# TODO: Edit the apache config automatically.
echo -e '\n\nAfter performing the above steps, please run setup_wsgi.sh as root:'
echo -e 'sudo ./setup_wsgi.sh'