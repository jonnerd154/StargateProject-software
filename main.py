#!/usr/bin/python3

"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""

import sys
import os
sys.path.append('classes')
sys.path.append('config')

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio
from StargateSG1 import StargateSG1

class GateApplication:
	
	def __init__(self):
	
		### Load our config file
		self.cfg = StargateConfig("config.json")

		### Setup the logger
		self.log = AncientsLogBook("sg1.log")

		### Check for new software updates ###
		self.swUpdater = SoftwareUpdate(self)
		if self.cfg.get("enableUpdates"):
			self.swUpdater.check_and_install()

		### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
		self.audio = StargateAudio(self)
		self.audio.set_correct_audio_output_device()

		### Create the Stargate object
		self.log.log('Booting up the Stargate! Version {}'.format(self.swUpdater.get_current_version()))
		self.stargate = StargateSG1(self)

	def run(self):
	
		# Keep the script running and monitor for updates with the update() method.
		self.stargate.update() #This will keep running as long as `stargate.running` is True.
		self.cleanup()
		
	def cleanup(self):
		
		# Release the ring when exiting. Just in case.
		stargate.ring.release()
		self.log.log('The Stargate program is no longer running')	
		quit()		

# Run the stargate application
app = GateApplication()
app.run()