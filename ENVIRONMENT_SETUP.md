# Flash the SD Card with Raspbian
1. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open the Imager, and click "Choose OS."
3. Click on "Raspberry Pi OS (Other)"
4. Select _Raspberry Pi OS Lite (32-bit)_ (At the time of this writing: Debian v11/"Bullseye:)
5. Click Choose Storage, and select your SD card.
6. Click "Write." Accept any warnings, and you may need to enter an Admin password for the computer you're working on.
7. When the process is complete, remove the SD card, and insert back *into the same computer*, _not_ the raspberry pi. We have one more thing to do before installing it in the Pi.

# Configure Wi-Fi
1. After reinserting the SD card, it should appear on your computer as a drive. Browse to that drive.
2. Create a new file with the below contents (substituting your Wi-Fi credentials) and save it to the root directory of the SD card. It must be named _exactly_ `wpa_supplicant.conf`:
```
country=us
update_config=1
ctrl_interface=/var/run/wpa_supplicant

network={
 scan_ssid=1
 ssid="NETWORK_SSID"
 psk="PASSWORD"
}
```
3. Eject the SD card, and reinstall it in your Raspberry Pi.

# Setup the Raspberry Pi Basics: Hardware, Users, SSH
1. Connect a keyboard and monitor to your Raspi. We will only need this to find the IP address, and enable SSH.
2. Power the Raspberry Pi and wait for it to boot (the green light will stop flickering).
3. At the login prompt, enter:
```
Username: pi
Password: raspberry
```
4. Determine the IP address and write it down.
```
ifconfig en0 | grep "inet "
```
5. Enable SSH:
 - Run `raspi-config`
 -    Select #3 (Interface Options) -> #2 SSH -> Enable
6. Enable SPI: `
 -    Select #3 (Interface Options) -> #4 SPI -> Enable
7. Enable I2C:
 -    Select #3 (Interface Options) -> #5 I2C -> Enable
8. Select "Finish" in the bottom-right corner to save.
9. Type `passwd` enter the current password (`raspberry`) and set the new password to "thestargateproject")
10. `sudo adduser sg1` Set the password to `sg1` and leave all misc questions (name, address, etc) blank.
11. Create a new file: `sudo nano /etc/sudoers.d/010_sg1-nopasswd`
   Paste this into it:
```
sg1 ALL=(ALL) NOPASSWD: ALL
```
11. Enable auto-login: `raspi-config` -> System Options -> S5 Boot / Auto Login -> B2 Console Autologin
12. Select "Finish" in the bottom-right corner to save. *The system will reboot!*
13. From your main computer, login to the Raspberry Pi via SSH:
```
IP Address: [as discovered above]
Username: sg1
Password: sg1
```
14. You should be connected via SSH! If so, you can disconnect the monitor and keyboard - we won't need them again.

# Update Software and Install System Dependencies
1. Update system packages:
```
sudo apt-get update -y
sudo apt-get upgrade -y
```
2. Install some packages
```
sudo apt-get install -y clang python3-dev python3-venv libasound2-dev avahi-daemon apache2 wireguard
```

# Create the virtual environment and install the basics
1. Create the virtual environment (do NOT use sudo!!):
```
python3 -m venv sg1_venv
```
2. Activate the virtual environment and install some dependencies
```
source sg1_venv/bin/activate
export CFLAGS=-fcommon
pip install setuptools
deactivate
```

# Upload the Stargate Software
1. Upload the software from the `/sg1` folder in Kristian's Archive Download to `/home/sg1/sg1`
2. If you're working from GitHub, be sure to upload the `soundfx` directory to `/home/sg1/sg1/soundfx`
3. Set execute permissions on the bash scripts:
```
chmod 774 /home/sg1/sg1/util/*
chmod 774 /home/sg1/sg1/scripts/*
```

# Install pip dependencies into the virtual environment:
Activate the virtual environment and install from `requirements.txt`
```
source sg1_venv/bin/activate
pip install -r sg1/requirements.txt
```

# Configure hostname / Bonjour
1. Update the `hosts` file to use "stargate" as a hostname.
```
sudo nano /etc/hosts
## Modify the `127.0.1.1` entry as below, then save the file:
  127.0.1.1 [tab] stargate
```
2. Update the OS' hostname config
`sudo nano /etc/hostname`
 - Modify the file to contain only `stargate` (no ticks), then save the file.

3. One more place to set the host name:
```
sudo hostname stargate
```
4. And reboot to take effect:
```
sudo reboot
```
5. When the Raspi comes back up you should be able to SSH to it via `stargate.local` instead of it's IP address.

# Configure Apache Web Server
1. Add Directory block and ModProxy config to `/etc/apache2/apache2.conf`:
`sudo nano `/etc/apache2/apache2.conf`
Add the below text after the other <Directory> blocks
```
<Directory /home/sg1/sg1/web>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
ProxyPass     /stargate/     http://localhost:8080/
```
2. Configure Apache to run the server as user and group `sg1`
`sudo nano /etc/apache2/envvars`
```
export APACHE_RUN_USER=sg1
export APACHE_RUN_GROUP=sg1
```
3. Configure the virtualhost DocumentRoot
`sudo nano /etc/apache2/sites-available/000-default.conf`
Update the existing `DocumentRoot` directive to read:
```
DocumentRoot /home/sg1/sg1/web
```
4. Enable ModProxy and ModProxyHTTP
```
cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/proxy.conf proxy.conf
sudo ln -s ../mods-available/proxy.load proxy.load
sudo ln -s ../mods-available/proxy_http.load proxy_http.load
```
5. Restart apache to load the new configs
```
sudo service apache2 restart
```
If there are no errors reported, congrats! It's probably working.
6. Test: In your browser, to go `http://stargate.local` (you MUST include the `http://`!!)
7. The page should load, and tell you that the Stargate is offline. That is okay - this shows that the Apache server is running, but the Stargate Software is not.

# Add a crontab entry to keep the speaker from turning off:
Edit `sg1`'s crontab:
`crontab -e` and add the following to the bottom of the file:
```
*/8 * * * * /home/sg1/sg1_venv/bin/python3 /home/sg1/sg1/scripts/speakerON.py
```

# Disable power management/savings on the wifi adapter:
```
sudo nano /etc/rc.local
## Above exit 0 add:
  /sbin/iw wlan0 set power_save off
```

# Disable the onboard audio adapter and configure the external audio adapter
1. Disable the onboard adapter
```
sudo nano /boot/config.txt
   # Change dtparam=audio=off
```
2. Configure ALSA to use the external audio adapter (OPTIONAL??)
```
sudo nano /usr/share/alsa/alsa.conf
   # Change to:
      defaults.ctl.card 1
      defaults.pcm.card 1
```

# Setup logrotated to rotate log files for better performance
1. Create a new file:
`sudo nano /etc/logrotate.d/stargate`

And copy this into it:
```
/home/sg1/sg1/logs/sg1.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}

/home/sg1/sg1/logs/database.log {
    missingok
    notifempty
    size 30k
    daily
    rotate 30
    create 0600 sg1 sg1
}
```
2. Force the logs to rotate now, to test:
`sudo logrotate --force /etc/logrotate.conf`

# Run the software (test mode)
1. `cd /home/sg1/sg1/ && sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/main.py`
2. Check the web interface. Is it working? Go to the info page - do the details load in? Hooray!

# Enable on-boot auto-run:
1. `sudo nano ~/.bashrc` Add to the end of the file:
```
myt=$(tty | sed -e "s:/dev/::")
if [ $myt = tty1 ]; then
  cd /home/sg1/sg1
  sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/main.py
fi
```
`sudo reboot`
2. When the raspi reboots, the software should automatically start.
