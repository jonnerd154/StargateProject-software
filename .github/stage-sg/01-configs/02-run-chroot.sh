#!/bin/bash -e

# Source functions.sh and install the rest of software
source /home/pi/sg1_v4/install/functions.sh
configure_git

echo 'Changing ownership of sg1_v4 to the first user'
cd /home/pi
sudo chown -R "${FIRST_USER_NAME}":"${FIRST_USER_NAME}" sg1_v4

set_permissions
init_venv

configure_apache
configure_crontab
disable_pwr_mgmt
disable_onboard_audio
configure_audio
configure_logrotate
configure_systemd_service
configure_wireguard
