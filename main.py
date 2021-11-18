#!/usr/bin/python3
import sys
import os
sys.path.append('classes')
sys.path.append('config')

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio

### Load our config file
cfg = StargateConfig()

"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""

### Setup the logger
log = AncientsLogBook()

### Check for new software updates ###
swUpdater = SoftwareUpdate(log)
if cfg.get("enableUpdates"):
	swUpdater.check_and_install()

### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
audio = StargateAudio(log)
audio.set_correct_audio_output_device()



# Create the Stargate object
log.log('Booting up the Stargate! Version {}'.format(swUpdater.get_current_version()))
import StargateSG1
stargate = StargateSG1(log)

# # Keep the script running and monitor for updates with the update() method.
# stargate.update() #This will keep running as long as stargate.running is True.
#
# # Release the ring when exiting. Just in case.
# stargate.ring.release()
#

# Exit
log.log('The Stargate program is no longer running')
