# StargateProject2021

# Running the Stargate Software
Log into the machine and type `sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/main.py`

# Running the Hardware Test Routine
Log into the machine and type `sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/test.py`

# To update from requirements.txt
```
source sg1_venv/bin/activate
pip install --upgrade pip
pip install -r sg1/requirements.txt
```

# Dial Aphopis's base with a keyboard
 - `cFX1K98A`

# Crontab
 - `*/8 * * * * /home/sg1/sg1_venv/bin/python3.8 /home/sg1/sg1/scripts/speakerON.py`

# To add Bonjour support (easy DNS)
```
sudo apt-get install avahi-daemon
sudo nano /etc/hosts
## Modify the `127.0.0.1` entry as below, then save the file:
  127.0.0.1 [tab] stargate

sudo hostname stargate

sudo reboot
```
When the Pi comes back up, you should be able to `ssh sg1@stargate.local`

# Install Apache Web Server
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install apache2 -y
```
- Add Directory block and ModProxy config to `/etc/apache2/apache2.conf`:
```
<Directory /home/sg1/sg1/web>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
ProxyPass     /stargate/     http://localhost:8080/
```
- Set the user/group for Apache to `sg1` (edit `/etc/apache2/envvars`)
```
export APACHE_RUN_USER=sg1
export APACHE_RUN_GROUP=sg1
```
- Configure the virtualhost DocumentRoot (edit `/etc/apache2/sites-available/000-default.conf`...edit exiting DocumentRoot directive)
```
DocumentRoot /home/sg1/sg1/web
```
- Enable ModProxy and ModProxyHTTP
```
cd /etc/apache2/mods-enabled
sudo ln -s ../mods-available/proxy.conf proxy.conf
sudo ln -s ../mods-available/proxy.load proxy.load
sudo ln -s ../mods-available/proxy_http.load proxy_http.load
```
- Restart apache to load the new configs
```
sudo service apache2 restart
```
