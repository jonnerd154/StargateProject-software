# Configuring the SD Card from Scratch
It is **highly** recommended to build your gate by using the pre-built Disk Image (ISO) provided by Kristian. Instructions for this EXPRESS SETUP PROCESS can be found in [EXPRESS_SETUP.md](../EXPRESS_SETUP.md)

**If you insist on doing things the hard way**, you can setup your own image from scratch. These instructions should help.

The majority of the installation is completed by a script at `sg1_v4/install/install.sh`, but we need to get the basics configured first.

## Flash the SD Card with Raspbian
1. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open the Imager, and click "Choose OS."
3. Click on "Raspberry Pi OS (Other)"
4. Select _Raspberry Pi OS Lite (32-bit)_ (At the time of this writing: Debian v11/"Bullseye")
5. Click Choose Storage, and select your SD card.
6. Click on the GEAR icon in the bottom right corner. Configure some settings:
  - Set Hostname: `YES` (`stargate`)
  - Enable SSH: `YES` (Use Password Authentication)
  - Set Username and Password: `YES`
    - Username: `pi`
    - Password: `sg1`
  - Configure wifi: `YES`
    - Enter your wifi AP credentials
    - Select your country code for Wi-Fi Compliance
  - Set Locale Settings: `YES`
    - Time Zone: Your timezone
    - Keyboard Layout: `US` (important for DHD functionality)
    - Skip First Run Wizard: `YES`
  - Click SAVE.
7. Click "Write." Accept any warnings, and you may need to enter an Admin password for the computer you're working on.
8. When the process is complete, remove the SD card and reinstall it in your Raspberry Pi
9. Power the Raspberry Pi and wait for it to boot (the green light will stop flickering)

## Connecting to the Pi for the first time
1. You need to find the Raspi's IP address. There are a few ways to do this:
  - Connect a monitor and keyboard, then run `ifconfig wlan0` and look for the IPv4 address after `inet`
  - Check the "attached devices" list in your router's Admin Panel
  - Use a network scanner app like [Fing](https://www.fing.com/)
2. Once you know the IP address, connect to the Pi via SSH and keep it open for later:
  - Windows: Use PuTTY
  - MacOS: Use Terminal: `ssh pi@YOURIPADDRESS`

Login credentials:
  ```
  Username: pi
  Password: sg1
  ```

## Copying the software bundle (git clone)
1. Clone the Repo: `sudo apt-get install git -y && cd ~ && git clone https://github.com/jonnerd154/StargateProject-software.git sg1_v4`

## Upload audio files (Via SCP)
1. Connect to the Pi using an SCP/SFTP file transfer client.
    - Windows: [WinSCP](https://winscp.net/eng/index.php) or [FileZilla](https://filezilla-project.org/download.php?type=client)
    - MacOS: [CyberDuck](https://cyberduck.io/) or [FileZilla](https://filezilla-project.org/download.php?type=client)
2. Copy the sound effects folder (Kristian's repo `/soundfx`) to the Raspi.
    - Copy the folder to `/home/pi/sg1_v4/soundfx`

## Prepare & Run the Installer
1. Go back to your SSH client and configure the Install Script's permissions:
```
sudo chmod u+x /home/pi/sg1_v4/install/*.sh
```
2. Run the installer and wait for it to complete. This could take up to 10 minutes. When it is complete, the Pi will reboot.
```
cd /home/pi/sg1_v4/install && ./install.sh
```
3. After the reboot, the Stargate software should start automatically. You'll hear a "we're ready to go"-type sound from the speaker when startup is complete. Comtrya!

## What's next?
- The installer setup [https://www.avahi.org/](avahi) and changed the hostname. You'll now be able to communicate with the Stargate with `stargate.local`, instead of it's IP address. For example:
```
ssh pi@stargate.local
```
- The installer changed the `pi` user's password. Your login credentials are now:
```
Username: pi
Password: sg1
```
- There is a web server running on the Stargate. You can access it in your favorite browser.

You'll need to type the whole `http://` part, or it will not work!
```
http://stargate.local
```
- *"What if I have multiple stargates on my network? Or want to call it something different?"*"
  - You can change the hostname with a simple command. In the command below, replace `YOURHOSTNAME` with your desired name for this gate (no symbols! Only A-z and 0-9). DO NOT include the `.local` part.:
  ```
  sudo raspi-config nonint do_hostname YOURHOSTNAME
  ```
- The Stargate Software will automatically start when the Raspi boots. It runs as a systemd daemon called `stargate.service`. If you want to manually start/stop/restart it, you can use these commands:
```
sudo systemctl start stargate.service
sudo systemctl stop stargate.service
sudo systemctl restart stargate.service
```
