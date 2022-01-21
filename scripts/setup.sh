#!/bin/bash

clear
echo
echo
echo "TheStargateProject: SG1 Version 4  -  Installer Script"
echo
echo

[ ! -d './sg1_v4' ] && echo "Upload the Software /home/sg1/sg1_v4/ before continuing" && exit 1
[ ! -d './sg1_v4/soundfx' ] && echo "Upload the Audio clips /home/sg1/sg1_v4/soundfx before continuing" && exit 1

echo 'V4 Software installation detected'

# Change the `pi` user password to "thestargateproject"
echo 'Setting pi user password'
sudo usermod --password $(echo thestargateproject | openssl passwd -1 -stdin) pi

# Add the `sg1` user and set password to "sg1"
echo 'Creating sg1 user'
sudo adduser sg1
echo 'Setting sg1 user password'
adduser --disabled-password --gecos "" sg1
sudo usermod --password $(echo sg1 | openssl passwd -1 -stdin) sg1

# Add sg1 to the no-password sudoers group
echo 'Adding sg1 user to password-less sudoers'
echo "sg1 ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/010_sg1-nopasswd

# Switch to the new sg1 user
echo 'Switching to the sg1 user'
sudo su sg1

# Enable SSH
echo 'Enabling SSH'
sudo raspi-config nonint do_ssh 1

# Enable SPI
echo 'Enabling SPI'
sudo raspi-config nonint do_spi 1

# Enable I2C
echo 'Enabling I2C'
sudo raspi-config nonint do_i2c 1

# Enable Boot/Autologin to Console Autologin
echo 'Configuring Auto Login via Console on Boot'
sudo raspi-config nonint do_boot_behaviour B2

# Update and Upgrade system packages
echo 'Updating, upgrading system packages...this may take a while.'
sudo apt-get update -y
sudo apt-get upgrade -y

# Install system-level dependencies
echo 'Installing system-level dependencies...this may take a while.'
sudo apt-get install -y clang python3-dev python3-venv libasound2-dev avahi-daemon apache2 wireguard

# Create the virtual environment
cd /home/sg1
echo 'Initializing Python virtual environment'
python3 -m venv sg1_venv_v4

# Activate the venv and install some dependencies
echo 'Installing pip setuptools into the virtual environment'
source sg1_venv_v4/bin/activate
export CFLAGS=-fcommon
pip install setuptools
deactivate

# Update the hostname to "stargate" so we can use "stargate.local" via Bonjour
echo 'Configuring hostname for stargate.local Bonjour'
sudo raspi-config nonint do_hostname stargate

# Set permissions on the scripts
echo 'Configuring permissions on Stargate Scripts'
sudo chmod 774 /home/sg1/sg1_v4/util/*
sudo chmod 774 /home/sg1/sg1_v4/scripts/*

# Activate the venv and install requirements.txt pip packages
echo 'Installing requirements.txt dependencies into the Virtual Environment'
source sg1_venv_v4/bin/activate
pip install -r sg1_v4/requirements.txt

## Configure Apache Web Server
# 1. Add Directory block and ModProxy config to `/etc/apache2/apache2.conf`:
# `sudo nano `/etc/apache2/apache2.conf`
# Add the below text after the other <Directory> blocks
# ```
# <Directory /home/sg1/sg1_v4/web>
#         Options Indexes FollowSymLinks
#         AllowOverride None
#         Require all granted
# </Directory>
# ProxyPass     /stargate/     http://localhost:8080/
# ```
# 2. Configure Apache to run the server as user and group `sg1`
# `sudo nano /etc/apache2/envvars`
# ```
# export APACHE_RUN_USER=sg1
# export APACHE_RUN_GROUP=sg1
# ```
# 3. Configure the virtualhost DocumentRoot
# `sudo nano /etc/apache2/sites-available/000-default.conf`
# Update the existing `DocumentRoot` directive to read:
# ```
# DocumentRoot /home/sg1/sg1_v4/web

# Enable ModProxy and ModProxyHTTP
echo 'Apache Config: Enabling required modules.'
cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/proxy.conf proxy.conf
sudo ln -s ../mods-available/proxy.load proxy.load
sudo ln -s ../mods-available/proxy_http.load proxy_http.load

#Restart apache to load the new configs
echo 'Apache Config: service restart to load configs.'
sudo service apache2 restart

# Add the speaker-tickler to our crontab
echo 'Configuring crontab (user: sg1)'
line="*/8 * * * * /home/sg1/sg1_venv_v4/bin/python3 /home/sg1/sg1_v4/scripts/speaker_on.py"
(crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -

## Disable power management/savings on the wifi adapter:
echo 'Disabling WiFi power management'
CONFIG="/etc/rc.local" #
sed -i -e '$i\\r\n/sbin\/iw wlan0 set power_save off\r\n' $CONFIG

# Disable the onboard audio adapter
echo 'Disabling RaspberryPi on-board audio adapter'
CONFIG="/boot/config.txt"
SETTING="off"
sed $CONFIG -i -r -e "s/^((device_tree_param|dtparam)=([^,]*,)*audio?)(=[^,]*)?/\1=$SETTING/"
if ! grep -q -E "^(device_tree_param|dtparam)=([^,]*,)*audio?=[^,]*" $CONFIG; then
  printf "dtparam=audio=$SETTING\n" >> $CONFIG
fi

# Configure ALSA to use the external audio adapter
echo 'Configuring ALSA to use external USB audio adapter'
CONFIG="/usr/share/alsa/alsa.conf" #
SETTING="1"
sed -i -e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" \
-e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" $CONFIG
sed -i -e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" \
-e "s/defaults\.pcm\.card [01]/defaults.pcm.card $SETTING/g" $CONFIG

# Load the logrotated configs
echo 'Configuring logrotate'
sudo cat <<EOF > /etc/logrotate.d/stargate
/home/sg1/sg1_v4/logs/sg1.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}

/home/sg1/sg1_v4/logs/database.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}
EOF

echo
echo
echo "Setup complete. The machine will now reboot."
echo
echo

sudo reboot
