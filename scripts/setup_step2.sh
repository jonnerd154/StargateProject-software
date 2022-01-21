# Switch to the new sg1 user
sudo su sg1

# Set permissions on the scripts
sudo chmod 774 /home/sg1/sg1_v4/util/*
sudo chmod 774 /home/sg1/sg1_v4/scripts/*

# Activate the venv and install requirements.txt pip packages
source sg1_venv_v4/bin/activate
pip install -r sg1_v4/requirements.txt

## Configure Apache Web Server
# 1. Add Directory block and ModProxy config to `/etc/apache2/apache2.conf`:
# `sudo nano `/etc/apache2/apache2.conf`
# Add the below text after the other <Directory> blocks
# ```
# <Directory /home/sg1/sg1/web>
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
# DocumentRoot /home/sg1/sg1/web

# Enable ModProxy and ModProxyHTTP
cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/proxy.conf proxy.conf
sudo ln -s ../mods-available/proxy.load proxy.load
sudo ln -s ../mods-available/proxy_http.load proxy_http.load

#Restart apache to load the new configs
sudo service apache2 restart

# Add the speaker-tickler to our crontab
line="*/8 * * * * /home/sg1/sg1_venv_v4/bin/python3 /home/sg1/sg1_v4/scripts/speaker_on.py"
(crontab -u $(whoami) -l; echo "$line" ) | crontab -u $(whoami) -

## Disable power management/savings on the wifi adapter:
#sudo nano /etc/rc.local
## Above exit 0 add:
#  /sbin/iw wlan0 set power_save off

# Disable the onboard adapter
#sudo nano /boot/config.txt
   # Change dtparam=audio=off

# Configure ALSA to use the external audio adapter
# sudo nano /usr/share/alsa/alsa.conf
#    # Change to:
#       defaults.ctl.card 1
#       defaults.pcm.card 1

# Load the logrotated configs
sudo cat /home/sg1/sg1_v4/logrotated.conf >> /etc/logrotate.d/stargate
