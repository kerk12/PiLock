#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
	echo "Script must be run as root"
	exit 1
fi

cp apacheconf/pilock.conf /etc/apache2/sites-available/pilock.conf
a2ensite pilock