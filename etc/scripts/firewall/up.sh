#!/bin/sh

/usr/sbin/iptables-restore /etc/scripts/firewall/ipv4.rules
/usr/sbin/ip6tables-restore /etc/scripts/firewall/ipv6.rules

