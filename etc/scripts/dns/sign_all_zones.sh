#!/bin/bash
set -e

cd /etc/bind/zones
dnssec-signzone -A -3 $(head -c 1000 /dev/random | sha1sum | cut -b 1-16) -N INCREMENT -o pieter-fiers.sb.uclllabs.be -t db.pieter-fiers.sb.uclllabs.be
