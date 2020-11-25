#!/bin/sh
if ! [ $(id -u) = 0 ]; then
   echo "This script must be run as root"
   exit 1
fi

cd /etc/scripts
. env/bin/activate
export PATH="/usr/sbin:$PATH"
certbot -n --agree-tos --expand --nginx --no-redirect --email pieter@pfiers.net \
        -d secure.pieter-fiers.sb.uclllabs.be \
        -d supersecure.pieter-fiers.sb.uclllabs.be \
	-d mx.pieter-fiers.sb.uclllabs.be \
	-d pieter-fiers.sb.uclllabs.be

