#!/bin/sh

iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

ip6tables -F
ip6tables -X
ip6tables -Z
for table in $(</proc/net/ip6_tables_names)
do
        ip6tables -t $table -F
        ip6tables -t $table -X
        ip6tables -t $table -Z
done
ip6tables -P INPUT ACCEPT
ip6tables -P OUTPUT ACCEPT
ip6tables -P FORWARD ACCEPT

