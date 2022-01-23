# Express Setup instructions
Express setup: all the cool kids are doing it! Completely headless (no keyboard/monitor required), and now with extra Calcium for strong bones.

It's a three step process:
```
1. Flash the SD card
2. Configure Wi-Fi
3. Kawoosh
```

## Flash the SD Card with Raspbian for Stargates
1. Download the ready-to-use Raspberry Pi Disk Image (.iso) file
In your browser, visit https://thestargateproject.com/stargate_images/sg1_v4.0.0.img.gz
2. Plug your SD card (8GB or larger) into your computer (MacOS or Windows)
3. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
4. Open the Raspberry Pi Imager, and click "Choose OS"
5. Scroll to the bottom of the list and select "Use custom"
6. In the file chooser, select the .iso file downloaded in step 1
7. Click Choose Storage, and select your SD card
8. Click "Write." Accept any warnings, and you may need to enter an Admin password for the computer you're working on
9. When the process is complete, remove the SD card, and insert back *into the same computer*, _not_ the raspberry pi. We have one more thing to do before installing it in the Pi: configure WiFi.

## Configure Wi-Fi
1. After reinserting the SD card, it should appear on your computer as a drive. Browse to that drive.
2. Inside, you'll find a file called `wpa_supplicant.conf.dist`. Make a copy of it, save it to the same folder, and call it `wpa_supplicant.conf`
 - It must be named _exactly_ `wpa_supplicant.conf`
 - Adjust the `country=` line to match your country (use the [ISO 2-letter abbreviation](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements), in lowercase. )
 - Replace `YOUR_NETWORK_SSID` and `YOUR_NETWORK_SSID` with your network's details. Your values should be enclosed in `"` (double quotes) *These are case-sensitive, and spaces matter!*
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
3. Eject the SD card, and reinstall it in your Raspberry Pi
4. Power the Raspberry Pi and wait for it to boot (the green light will stop flickering)
5. You'll hear a "we're ready to go"-type sound from the speaker when startup is complete. Comtrya!

## What's next?
- There is a web server running on the Stargate. You can access it in your favorite browser. You'll need to type the whole `http://` part, or it will not work!

       [http://stargate.local](http://stargate.local)

- Your SSH login credentials are now:
```
Host: stargate.local
Username: pi
Password: sg1
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
