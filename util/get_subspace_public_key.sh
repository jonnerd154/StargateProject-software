#!/bin/bash

# Checks if wireguard already has a public key
# If it does, we print the existing key
# If not, we generate a new public key, and print it

FILE=/etc/wireguard/publickey

if sudo test -f "$FILE"; then
    sudo su -c "cat /etc/wireguard/publickey"
else
    sudo su -c "cd /etc/wireguard/; umask 077; wg genkey | tee privatekey | wg pubkey > publickey; cat publickey"
fi

exit 0