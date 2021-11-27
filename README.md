# StargateProject2021

# Running the Stargate Software
Log into the machine and type `sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/main.py`

# Running the Hardware Test Routine
Log into the machine and type `sudo /home/sg1/sg1_venv/bin/python /home/sg1/sg1/test.py`

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

sudo nano /etc/hostname
## replace the contents with the same name as above (stargate)
sudo reboot
```
When the Pi comes back up, you should be able to access the web console by navigating to:
`http://stargate.local/testing.htm`
