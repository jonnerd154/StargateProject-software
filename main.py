#!/usr/bin/python3
import sys
import os
sys.path.append('classes')
sys.path.append('config')

from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio

"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""

### Check for new software updates ###
swUpdater = SoftwareUpdate()
swUpdater.check_and_install()

### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
audio = StargateAudio()
audio.set_correct_audio_output_device()

log = AncientsLogBook()
#
# # Create the Stargate object
# log('sg1.log', f'Booting up the Stargate! Version {version}')
# print (f'Booting up the Stargate! Version {version}')
# import StargateSG1
# stargate = StargateSG1()
#
# # Keep the script running and monitor for updates with the update() method.
# stargate.update() #This will keep running as long as stargate.running is True.
#
# # Release the ring when exiting. Just in case.
# stargate.ring.release()
#

# Exit
print('Exiting')
log('The Stargate program is no longer running')
