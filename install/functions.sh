
function wait_for_enter () {
  echo "Done. Press any key to continue"
  while [ true ] ; do
  read -t 3 -n 1
  if [ $? = 0 ] ; then
  exit
  fi
  done
}

function verify_stargate_software_or_exit() {
  [ ! -d '../classes' ] && echo "Upload the Software /home/pi/sg1_v4/ before continuing" && exit 1
  [ ! -d '../soundfx' ] && echo "Upload the Audio clips /home/pi/sg1_v4/soundfx before continuing" && exit 1
  echo 'Version 4.x Software installation detected'
}

function enable_ssh() {
  # Enable SSH
  echo 'Enabling SSH'
  sudo raspi-config nonint do_ssh 0
}

function copy_wpa_supplicant() {
  # Create a template wpa_supplicant.
  echo 'Copying wpa_supplicant.conf.dist to /boot'
  sudo rm -Rf /boot/wpa_supplicant.conf.dist
  sudo cp ~/sg1_v4/install/wpa_supplicant.conf.dist /boot/
}

function config_users_and_passwords() {
  # Change the `pi` user password to "sg1"
  echo 'Setting pi user password'
  sudo usermod --password $(echo sg1 | openssl passwd -1 -stdin) pi

  # # Add the `sg1` user and
  # echo 'Creating sg1 user'
  # sudo adduser sg1
  #
  # # Set password to "sg1"
  # echo 'Setting sg1 user password'
  # sudo adduser --disabled-password --gecos "" sg1
  # sudo usermod --password $(echo sg1 | openssl passwd -1 -stdin) sg1

  # Add sg1 to the no-password sudoers group
  # echo 'Adding sg1 user to password-less sudoers'
  # echo "sg1 ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/010_sg1-nopasswd
}

function set_permissions() {
  # Set permissions on the scripts
  echo 'Configuring permissions on Stargate Scripts'
  sudo chmod u+x /home/pi/sg1_v4/util/*
  sudo chmod u+x /home/pi/sg1_v4/scripts/*
}

function do_hardware_config() {
  # Enable SPI
  echo 'Enabling SPI'
  sudo raspi-config nonint do_spi 0

  # Enable I2C
  echo 'Enabling I2C'
  sudo raspi-config nonint do_i2c 0

  # Enable Boot/Autologin to Console Autologin
  echo 'Configuring Auto Login via Console on Boot'
  sudo raspi-config nonint do_boot_behaviour B2
}

function apt_update_and_install() {
  # Update and Upgrade system packages
  echo 'Updating, upgrading system packages...this may take a while.'
  sudo apt-get update -y | sed 's/^/     /'
  sudo apt-get upgrade -y | sed 's/^/     /'

  # Install system-level dependencies
  echo 'Installing system-level dependencies...this may take a while.'
  sudo apt-get install -y clang python3-dev python3-venv libasound2-dev avahi-daemon apache2 wireguard | sed 's/^/     /'
}

function init_venv() {
  # Create the virtual environment
  cd /home/pi
  rm -Rf /home/pi/sg1_venv_v4
  echo 'Initializing Python virtual environment'
  python3 -m venv sg1_venv_v4

  # Activate the venv and install some dependencies
  echo 'Installing pip setuptools into the virtual environment'
  source sg1_venv_v4/bin/activate
  export CFLAGS=-fcommon
  pip install setuptools | sed 's/^/     /'

  # Install requirements.txt pip packages
  echo 'Installing requirements.txt dependencies into the Virtual Environment'
  source sg1_venv_v4/bin/activate
  pip install -r sg1_v4/requirements.txt | sed 's/^/     /'

  echo "Deactivating the virtual environment"
  deactivate
}

function configure_hostname() {
  # Update the hostname to "stargate" so we can use "stargate.local" via Bonjour
  echo 'Configuring hostname for stargate.local Bonjour'
  sudo hostnamectl set-hostname stargate # Sets hostname temporarily and for the current session
  sudo raspi-config nonint do_hostname stargate # Sets hostname permanently
}

function configure_apache() {

  echo 'Apache Web Server Config: Start'
  echo 'Adding Stargate API Apache Configuration'
  sudo tee -a /etc/apache2/conf-available/stargate_api.conf > /dev/null <<EOT
<Directory /home/pi/sg1_v4/web>
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
ProxyPass     /stargate/     http://localhost:8080/
EOT

  echo 'Enabling Stargate API Apache Configuration'
  sudo ln -sf /etc/apache2/conf-available/stargate_api.conf /etc/apache2/conf-enabled/stargate_api.conf

  echo 'Configuring Apache to run the server as user and group ''sg1'''
  sudo sed -i "s/export APACHE_RUN_USER=www-data/export APACHE_RUN_USER=pi/" /etc/apache2/envvars
  sudo sed -i "s/export APACHE_RUN_GROUP=www-data/export APACHE_RUN_GROUP=pi/" /etc/apache2/envvars

  echo 'Configure the virtualhost DocumentRoot'
  sudo sed -i "s|\("DocumentRoot" * *\).*|\1/home/pi/sg1_v4/web|" /etc/apache2/sites-available/000-default.conf

  # Enable ModProxy and ModProxyHTTP
  echo 'Apache Config: Enabling required modules.'
  cd /etc/apache2/mods-enabled
  sudo ln -sf ../mods-available/proxy.conf proxy.conf
  sudo ln -sf ../mods-available/proxy.load proxy.load
  sudo ln -sf ../mods-available/proxy_http.load proxy_http.load

  restart_apache
}

function restart_apache() {
  #Restart apache to load the new configs
  echo 'Apache Config: service restart to load configs.'
  sudo service apache2 restart
}

function configure_crontab() {
  # Add the speaker-tickler to our crontab
  echo 'Configuring crontab (user: pi)'
  (crontab -l; echo "*/8 * * * * /home/pi/sg1_venv_v4/bin/python3 /home/pi/sg1_v4/scripts/speaker_on.py")|awk '!x[$0]++'|crontab -
}

function disable_pwr_mgmt() {
  ## Disable power management/savings on the wifi adapter:
  CONFIG="/etc/rc.local"
  if grep -Fq '/sbin/iw wlan0 set power_save off' $CONFIG
  then
      echo 'WiFi power management is already disabled'
  else
      echo 'Disabling WiFi power management'
      sudo sed -i '$i\\r\n/sbin\/iw wlan0 set power_save off\r\n' $CONFIG
  fi
}

function disable_onboard_audio() {
  # Disable the onboard audio adapter
  sudo cp /boot/config.txt /boot/config.bak
  echo 'Disabling RaspberryPi on-board audio adapter'
  CONFIG="/boot/config.txt"
  SETTING="off"
  sudo sed $CONFIG -i -r -e "s/^((device_tree_param|dtparam)=([^,]*,)*audio?)(=[^,]*)?/\1=$SETTING/"
  if ! grep -q -E "^(device_tree_param|dtparam)=([^,]*,)*audio?=[^,]*" $CONFIG; then
    echo "pattern not found, creating"
    printf "dtparam=audio=$SETTING\n" >> $CONFIG
  fi
}

function configure_audio() {
  # Configure ALSA to use the external audio adapter
  echo 'Configuring ALSA to use external USB audio adapter'
  CONFIG="/usr/share/alsa/alsa.conf" #
  TEMP="alsa.temp"
  SETTING="1"
  sudo cp $CONFIG $TEMP
  sudo sed -i -e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" \
  -e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" $TEMP
  sudo sed -i -e "s/defaults\.ctl\.card [01]/defaults.ctl.card $SETTING/g" \
  -e "s/defaults\.pcm\.card [01]/defaults.pcm.card $SETTING/g" $TEMP
  sudo mv $TEMP $CONFIG
}

function configure_logrotate() {
  # Load the logrotated configs
  echo 'Configuring logrotate'
  sudo tee -a /etc/logrotate.d/stargate > /dev/null <<EOT
/home/pi/sg1_v4/logs/sg1.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}

/home/pi/sg1_v4/logs/database.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}
EOT
}
