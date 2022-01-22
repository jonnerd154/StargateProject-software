# Configuring the SD Card from Scratch
It is _highly_ recommended to build your gate by using the pre-built Disk Image (ISO) provided by Kristian. Instructions to download that are in the Archive Download.

If you wish to set up your own image, these instructions should help.

## Flash the SD Card with Raspbian
1. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Open the Imager, and click "Choose OS."
3. Click on "Raspberry Pi OS (Other)"
4. Select _Raspberry Pi OS Lite (32-bit)_ (At the time of this writing: Debian v11/"Bullseye")
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
 ssid="YOUR_NETWORK_SSID"
 psk="YOUR_PASSWORD"
}
```
3. Create a blank file at `/boot/ssh` to enable SSH
4. Eject the SD card, and reinstall it in your Raspberry Pi.
5. Power the Raspberry Pi and wait for it to boot (the green light will stop flickering).

## Connecting to the Pi for the first time
1. You need to find the Raspi's IP address.
  - Check the "attached devices" list in your router's Admin Panel
  - Use a network scanner app like Fing
  - Connect a monitor and keyboard, then run `ifconfig` and look for the IP address under `wlan0`
2. Once you know the IP address, connect to the Pi via SSH:
  - Windows: Use PuTTY
  - MacOS: Use Terminal `ssh pi@YOURIPADDRESS`
  Default login credentials (NOTE: password will change to `sg1` after installation):
  ```
  Username: pi
  Password: raspberry
  ```

## Copying the Software bundle
1. Connect to the Pi using an SCP file transfer client.
  - Windows: [WinSCP](https://winscp.net/eng/index.php) or [FileZilla](https://filezilla-project.org/download.php?type=client)
  - MacOS: [CyberDuck](https://cyberduck.io/) or [FileZilla](https://filezilla-project.org/download.php?type=client)
2. Copy the software folder (Kristian's repo `/sg1_v4`) to the Raspi.
  - Copy it to `/home/pi/sg1_v4`
  - To verify, when you are done, the main readme file should be at `/home/pi/sg1_v4/README.md`

## Prepare & Run the Installer
1. Go back to your SSH client and configure the Install Script's permissions:
```
sudo chmod u+x /home/pi/sg1_v4/install/*.sh
```
2. Run the installer and wait for it to complete. This could take up to XX minutes. When it is complete, the Pi will reboot.
```
sudo /home/pi/sg1_v4/install/install.sh
```
