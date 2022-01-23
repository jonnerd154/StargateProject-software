#!/bin/bash

clear
echo
echo
echo 'TheStargateProject: SG1 Version 4  -  Installer Script'
echo
echo

source functions.sh
#set -o xtrace

echo 'Starting...'
verify_stargate_software_or_exit

enable_ssh
configure_hostname
copy_wpa_supplicant
config_users_and_passwords

set_permissions
do_hardware_config
apt_update_and_install
init_venv

configure_apache
configure_crontab
disable_pwr_mgmt
disable_onboard_audio
configure_audio
configure_logrotate
configure_systemd_service

echo
echo
echo 'Setup complete. The machine will now reboot.'
echo
echo ' Connect via SSH: `ssh pi@stargate.local`'
echo ' Open the web interface `http://stargate.local`'
echo
echo
sudo reboot
