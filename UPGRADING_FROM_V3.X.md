# Upgrading from v3.x
If you already have a Stargate built and running, you'll want to copy some configurations over from the old gate/SD card. You'll need to do this via SCP while the old SD card is still installed in your gate. If you have a second SD card, it would be a good idea to flash the spare card, so you don't destroy your known-good card.

** **DO NOT REFLASH YOUR EXISTING SD CARD UNTIL FOLLOWING THESE INSTRUCTIONS!** **

1. Using SCP, copy these files from your old gate, and keep them on a computer. You will need them to configure the new Stargate software.
```
/etc/wireguard/subspace.conf
/etc/wireguard/privatekey
/etc/wireguard/publickey
/home/sg1/sg1/stargate_address.py
/home/sg1/sg1/chevrons.py
```
2. Flash the SD Card.
  - It is _highly_ recommended to build your gate by using the pre-baked Disk Image (ISO) provided by Kristian. Instructions to download that are in the Archive Download. Or you can roll your own by following the instructions in [/ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md).
  - To Flash the SD card with the pre-baked disk image, follow the instructions in [/EXPRESS_SETUP.md](EXPRESS_SETUP.md)

3. With the newly prepared SD card installed in your Raspi, upload the following you downloaded to your computer from the old gate to the new Gate, into the same locations that you copied them from:
```
/etc/wireguard/subspace.conf
/etc/wireguard/privatekey
/etc/wireguard/publickey
```
4. The first time the V4 software starts, it will initialize it's config files from default configurations.
You can modify them to match your custom configuration. You'll find them in:
_Be careful when editing!_ If the file doesn't contain valid JSON, the software won't start.
- `/home/pi/sg1_v4/config/addresses.json` - adjust `local_stargate_address` (from old /home/sg1/sg1/stargate_address.py)
- `/home/pi/sg1_v4/config/config.json` - adjust `chevron_mapping` (from old /home/sg1/sg1/chevrons.py)
5. After changing these configurations, restart the Stargate software to load the new values:
```
sudo systemctl restart stargate.service
```
