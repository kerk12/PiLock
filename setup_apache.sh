#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
	echo "Script must be run as root"
	exit 1
fi

echo 'Installing required packages'

apt-get update
apt-get -y install apache2 libapache2-mod-wsgi python-pip
a2enmod wsgi
pip install -r requirements.txt

mkdir /etc/apache2/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/pilock.key -out /etc/apache2/ssl/pilock.crt
chmod -R 400 /etc/apache2/ssl
a2enmod ssl


echo -e 'A Self-Signed Certificate has been created. You now need to configure Apache to work with that certificate.'
echo -e 'For more info: \n https://hallard.me/enable-ssl-for-apache-server-in-5-minutes/'
echo -e 'We also STRONGLY recommend that you enable HSTS, in order to prevent SSL Stripping.'
echo -e '\n\nAfter performing the above steps, please run setup_wsgi.sh as www-data:'
echo -e 'sudo -u www-data ./setup_wsgi.sh'
