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
If you used non-default chevron mappings (or other changes!) when building your 'gate, you'll need to adjust the new configuration as well
- `/home/pi/sg1_v4/config/milkyway-addresses.json` - adjust `local_stargate_address` with values from from your old `/home/sg1/sg1/stargate_address.py`

5. Open the web interface (http://stargate.local), go to `Admin`-->`Configuration`. Scroll down to the "Chevron GPIO Configurations" section. Copy the configurations into the appropriate fields, then press enter or scroll to the bottom and click "submit." Your changes will be confirmed in a dialog box.

To interpret the old configuration file, see these examples:

|  Line in V3 Config   | Chevron Number | Chevron Config LED Pin   | Chevron Config Motor Number |
| -------------------- | ---------------|------------------------- | --------------------------- |
| `1: Chevron(21, 3)`  |      1         |           21             |          3                  |
| `2: Chevron(16, 4)`  |      2         |           16             |          4                  |


6. Restart the Stargate software to load the new configuration:
In the web interface, go to `Admin`-->`Restart Software`. Click YES to confirm.
After about 10 seconds you should hear one of the team members tell you the gate is ready.

7. **"Trust but Verify"**
- After adjusting the configurations we suggest testing individual Chevrons to confirm everything is correct. In the web interface, go to `Admin`-->`Testing / Debug`. In here you will find buttons that allow you to test all of the hardware. First, scroll down to the "Cycle Chevrons" section. Clicking one of these buttons will simulate a full unlock/light on/lock sequence for each chevron. You want to verify that:
  - The Chevrons activate in the correct sequence (see Kristian's site for details).
  - The Chevron moves "down" first, then turns it's light on, then moves up and the light stays on.
  - Sound accompanies the actions and appears to be in sync.

- You can experiment with other controls in here too - the "Simulate Incoming Wormhole" button is particularly fun.

- Next, we need to verify that the Gate is on the Subspace network. In the web interface, go to `Admin-->System Information`. In here you'll see a bunch of information about your gate. Verify that:
  - **Stargate Name:** [ _Your Stargate's Name as recorded with Kristian's servers_ ]
  - **Local Stargate Address:** [ _Your Stargate's Address as recorded with Kristian's servers_ ]
  - **Subspace Status:** *ONLINE*
  - **Subspace Public Key:** [ _Your Public Key, as loaded from the V3 config file_ ]
  - **Subspace IP Address:** [ _some IP_ ]
  - **Internet Connection:** *Connected*

8. **Dial!** If everything above looks good, you're ready to try dialing another Subspace-connected Stargate. In the web interface, go to `Address Book`. Click on one of the BLUE buttons to select a Subspace gate and watch the gate do it's thing! Remember, there is a chance that stargate is not currently online, so don't get discouraged if it doesn't work. Kristian's second gate, `Abythres` or `Abythres 2` is almost always online and makes a good test.
