## New in version 4.0.0
This version is a major upgrade from the v3.x branch. Completely refactored and with a lot of exciting new functionality and opportunities to extend the existing functionality!

- Vastly improved setup and installation process - quick and easy!
- Added web interface to dial, see what planet an incoming wormhole is from, run tests, and more
  - Dialing by pressing symbol buttons in a web browser
  - Dialing by clicking on an entry in the Address Book (both Movie Gates, and Fan Gates)
  - Shows what type of wormhole (incoming/outgoing), if any, and what planet is connected
  - Shows the approximate time-to-disengage (~38 minutes max)
  - Dialing a black hole is dangerous - you shouldn't do that. But if you did it's dangerous. You've been warned!!
  - Testing functions:
    - Cycle Chevrons individually
    - Move the symbol ring
    - Turn on ALL of the chevron LEDs
    - Turn off ALL of the LEDs on the Gate
    - Instantly open a wormhole
    - Close any open wormhole
    - Simulate an incoming wormhole (most requested feature)
  - Administrative functions:
    - Volume up/down (+/-5%/click) Volume level is saved and persists between reboots
    - Reboot the Raspberry Pi
    - Shutdown the Raspberry Pi (no more dirty shutdowns!)
  - In-App Subspace Network configuration: no more typing commands in SSH!
  - Shows helpful debug information, internet & subspace connection status, and software update information.
  - UI works pretty well on Mobile Devices, too.
- The software will run as normal even if hardware isn't connected or is not connected correctly. The gate will degrade to a "hardware simulation" state, where everything works as it should, just without actually controlling the hardware.
- Startup and shutdown are now graceful, and the software cleans up it's threads on exit.
- Completely restructured the code for readability, adherence to industry standards, and facilitating further extension of the software.
- Added JSON configuration files to allow easy, dynamic reconfiguration (a future version is planned to have this capability available in the web interface)
- Switched to a web API method for retrieving Fan Gates and Software Updates - previously done via SQL server direct query.
- Fan Gates are automatically updated every 30 minutes. Previously required a reboot
- Software Updates are checked every 24 hours. Previously required a reboot.
- Software now runs as a systemd daemon. Manage the daemon with these commands:
```
sudo systemctl start stargate.service
sudo systemctl stop stargate.service
sudo systemctl restart stargate.service
sudo systemctl status stargate.service
```
- Added `avahi` / `Bonjour` so the 'Gate can be accessed as `stargate.local` - you don't need to know it's IP address anymore!
- Adopted SemVer versioning
- Fully documented the Web API
- Code is linted with pylint
- Lots of behind the scenes stuff to make development, extension and debugging easier
- Installation script and pre-prepared disk image (for the Raspi 3B+) make installation a breeze
- Adds the Stargate Loopback Address (27, 7, 15, 1, 2), analogous with 127.0.0.1 to allow simulating incoming wormholes
- Security enhancements
- Better exception handling to prevent crashes
- Improved memory management
- Added firewall (UFW) to limit access. This is redundant and complementary to the firewalling that occurs on the Subspace Network Server.
- Added logrotate, so log files don't get huge and slow things down or fill up the drive. Retains 30 days of daily log file backups, FIFO.
- Automatic configuration of the audio devices to prevent snafus.

## FEATURES on the backlog for possible future development
  - Scheduled Iris open/closed times
  - Scheduled mute times
  - Button in Web to open/close the Iris
  - Button in Web to connect/disconnect from subspace
  - HardwareStatus API, to be able to ascertain the chevron positions (locked/unlocked--up/down), LED states, and glyph ring position/movement/speed/direction.
  - Incoming wormhole alert in Web
  - Configure WiFi via Bluetooth (WebBluetooth in a browser), so you can skip the wpa_supplicant part of setup.
  - Implement homing
  - Support for Stargate Main Board...for whenever the semiconductor gods look favorably upon our village.
  - Configuration editing in Web UI
  - More Web stuff: fun interfaces, alternate "keyboard layouts," hidden movie references, etc.
  - Upload your own, additional sound clips
  - Play sound clips by clicking buttons in the Web UI
  - "Call Log" in Web: Shows last 25 incoming and outgoing wormholes, duration established, and what planet.
  - Show log files in Web (WebSocket streaming?)
  - Consider moving API away from polling to use WebSockets? Polling was just the quick/easy way out.


## New in version 3.7:
- The Stargate server will now also start with eth0 interface only. (If subspace or wlan is missing)

## New in version 3.6:
- DHD detection update. Planet/stargate name is used in the log instead of the IP.

## New in version 3.5:
- Fix an issue with audio output. The program will now edit the alsa.conf file to set the USB audio adapter as output.
