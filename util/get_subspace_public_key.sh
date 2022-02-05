#!/bin/bash

# Checks if wireguard already has a public key
# If it does, we print the existing key
# If not, we generate a new public key, and print it

if [[ "$OSTYPE" == "darwin"* ]]; then
  WGROOT=/usr/local/etc/wireguard/ # For MacOS
else
  WGROOT=/etc/wireguard/ # For Raspi
fi

# Verify that WGROOT is a valid path
if [ -d $WGROOT ]; then
  echo "WireGuard is not installed"
  exit 1
fi

# Verify that we have wg installed
which wg
if [ $? -eq 1 ]; then
  echo "WireGuard is not installed"
  exit 1
fi

if sudo test -f "$WGROOT"/publickey; then
    sudo cat $WGROOT/publickey
else
  sudo su root -c "cd "$WGROOT"; umask 077; wg genkey | tee privatekey | wg pubkey > publickey; cat publickey"
fi

exit 0
