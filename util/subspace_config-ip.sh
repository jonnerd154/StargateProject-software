#!/bin/bash

# Adds and sets up the "subspace" interface in WireGuard (VPN Client)
# Configures the static IP from vargs
# Saves the configuration
# Enables the subspace interface to run in default Unix running modes
# Reboots the machine - currently commented out!

echo "Configuring Subspace Network"

if [[ "$OSTYPE" == "darwin"* ]]; then
  WGROOT=/usr/local/etc/wireguard/ # For MacOS
  exit 0 # This script doesn't currently work for MacOS - just return w/o action for now.
else
  WGROOT=/etc/wireguard/ # For Raspi
fi

if [ -z "$1" ]
then
 echo "No IP Address provided"
 exit 1
fi

sudo su root -c "cd "$WGROOT"; wg-quick up subspace; wg set subspace private-key privatekey;"
sudo su root -c "ip addr add $1 dev subspace wg-quick save subspace"
sudo su root -c "systemctl enable wg-quick@subspace"

# TODO: This process needs to change on MacOS - the executables are different.
echo "Configuration saved. Please reboot the Raspi (sudo reboot)."
#sudo reboot

exit 0
