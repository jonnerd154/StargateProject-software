#!/bin/bash

# Adds and sets up the "subspace" interface in WireGuard (VPN Client)
# Configures the static IP from vargs
# Saves the configuration
# Enables the subspace interface to run in default Unix running modes
# Reboots the machine

echo "Configuring Subspace Network"

if [ -z "$1" ] 
then
 echo "No IP Address provided"
 exit 1
fi

sudo su -c "cd /etc/wireguard/; wg-quick up subspace; wg set subspace private-key privatekey;"
sudo su -c "ip addr add $1 dev subspace wg-quick save subspace"
sudo su -c "systemctl enable wg-quick@subspace"
sudo reboot
echo "Subspace configured"
exit 0