#!/bin/bash

if [ $# != 3 ]; then
        exit "usage: $0 <directory-path> <key-size> <expiry-days>"
        exit 1
fi

#
# there seemed to be a prob with it stuck in a stty sane wait which was cured by 
# adding the -nottyinit/-nottycopy option on my production server ...
#

echo openssl genrsa -des3 -out "$1/x509.key" $2
echo openssl rsa -in "$1/x509.key" -out "$1/x509.keydec"
echo openssl rsa -in "$1/x509.key" -pubout -out "$1/x509.pub"
echo openssl req -new -x509 -days $2 -key "$1/x509.key" -out "$1/x509.crt"


