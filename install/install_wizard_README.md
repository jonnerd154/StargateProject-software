# Configuring the SD Card from Scratch
It is _highly_ recommended to build your gate by using the pre-built Disk Image (ISO) provided by Kristian. Instructions to download that are in the Archive Download.

If you wish to set up your own image, these instructions should help.

## Flash the SD Card with Raspbian
1. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open the Imager, and click "Choose OS."
3. Click on "Raspberry Pi OS (Other)"
4. Select _Raspberry Pi OS Lite (32-bit)_ (At the time of this writing: Debian v11/"Bullseye:)
5. Click Choose Storage, and select your SD card.
6. Click "Write." Accept any warnings, and you may need to enter an Admin password for the computer you're working on.
7. When the process is complete, remove the SD card, and insert back *into the same computer*, _not_ the raspberry pi. We have one more thing to do before installing it in the Pi.

## Configure Wi-Fi & enable SSH
1. After reinserting the SD card, it should appear on your computer as a drive. Browse to that drive.
2. Create a new file with the below contents (substituting your Wi-Fi credentials) and save it to the root directory of the SD card's `/boot` partition. It must be named _exactly_ `wpa_supplicant.conf`:
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
3. Create a blank file at `/boot/ssh` to enable SSH
4. Eject the SD card, and reinstall it in your Raspberry Pi.

## Copying the Software bundle
1. Power the Raspberry Pi and wait for it to boot (the green light will stop flickering).
2. Find the Raspi's IP address. You can use the mobile app "Fing" or look at your router's "attached devices" section.
3. For this first connection, we will use the default raspi login credentials. They will change during the installation process.
```
Username: pi
Password: raspberry
```
4. Using an SCP file transfer client (FileZilla, CyberDuck, etc), copy the software to the Raspi.
```Copy it to /home/pi/sg1_v4
When you are done, the main readme file should be at /home/pi/sg1_v4/README.md
```
5. Connect to the Raspi via SSH (MacOS Terminal or PuTTY), using the above credentials.
6. Configure the Install Script's permissions and run it
```
sudo chmod u+x /home/pi/sg1_v4/install/*.sh
sudo /home/pi/sg1_v4/install/install.sh
