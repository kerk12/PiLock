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

mkdir /etc/apache2/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout pilock.key -out pilock.crt
a2enmod ssl
