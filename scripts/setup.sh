#!/bin/bash

echo
echo
echo "Upload the Software and audio files to /home/sg1_v4/ before continuing"
echo
echo

# Change the `pi` user password to "thestargateproject"
sudo usermod --password $(echo thestargateproject | openssl passwd -1 -stdin) pi

sudo adduser sg1
# Add the `sg1` user and set password to "sg1"

adduser --disabled-password --gecos "" sg1
sudo usermod --password $(echo sg1 | openssl passwd -1 -stdin) sg1

# Add sg1 to the no-password sudoers group
echo "sg1 ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/010_sg1-nopasswd

# Enable SSH
sudo raspi-config nonint do_ssh 1

# Enable SPI
sudo raspi-config nonint do_spi 1

# Enable I2C
sudo raspi-config nonint do_i2c 1

# TODO: Enable Boot/Autologin to Console Autologin

# Switch to the new sg1 user
sudo su sg1

# Update and Upgrade system packages
sudo apt-get update -y
sudo apt-get upgrade -y

# Install system-level dependencies
sudo apt-get install -y clang python3-dev python3-venv libasound2-dev avahi-daemon apache2 wireguard

# Create the virtual environment
cd /home/sg1
python3 -m venv sg1_venv_v4

# Activate the venv and install some dependencies
source sg1_venv_v4/bin/activate
export CFLAGS=-fcommon
pip install setuptools
deactivate

# Update the hostname to "stargate" so we can use "stargate.local" via Bonjour
sudo raspi-config nonint do_hostname stargate

echo
echo
echo "The machine will reboot now. When it comes back up, login as sg1 and run setup_step2.sh."
echo
echo

sudo reboot
