#!/usr/bin/python3

"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""

import sys
import os
sys.path.append('classes')
sys.path.append('config')

from http.server import HTTPServer
import threading
import atexit

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio
from stargate_sg1 import StargateSG1
from web_server import StargateWebServer
from electronics import Electronics

class GateApplication:

	def __init__(self):

		dirname, filename = os.path.split(os.path.abspath(__file__))
		self.base_path = dirname

		### Load our config file
		self.cfg = StargateConfig(self.base_path, "config.json")

		### Setup the logger
		self.log = AncientsLogBook(self.base_path, "sg1.log")

		### Detect our electronics and initialize the hardware
		#self.electronics = ElectronicsNone(self)
		self.electronics = Electronics(self).hardware

		### Check/set the correct USB audio adapter. This is necessary because different raspberries detects the USB audio adapter differently.
		self.audio = StargateAudio(self, self.base_path)
		self.audio.set_correct_audio_output_device()

		### Check for new software updates ###
		self.swUpdater = SoftwareUpdate(self)
		if self.cfg.get("enableUpdates"):
			self.swUpdater.check_and_install()

		### Create the Stargate object
		self.log.log('Booting up the Stargate! Version {}'.format(self.swUpdater.get_current_version()))
		self.stargate = StargateSG1(self)

		### Start the web server
		self.log.log('Starting web server...')
		StargateWebServer.stargate = self.stargate
		self.httpd_server = HTTPServer(('', 80), StargateWebServer)
		self.httpd_thread = threading.Thread(name="stargate-http", target=self.httpd_server.serve_forever)
		self.httpd_thread.daemon = True
		self.httpd_thread.start()

		### Register atexit handler
		atexit.register(self.cleanup) # Ensure we handle cleanup before quitting, even on exception

	def run(self):
		self.stargate.update() #This will keep running as long as `stargate.running` is True.

	def cleanup(self):
		self.stargate.ring.release()      # Release the ring when exiting. Just in case.
		self.stargate.wh.clear_wormhole() # Clear the wormdhole LEDs
		
		self.httpd_server.shutdown()
		self.stargate.cleanup()

		self.log.log('The Stargate program is no longer running')
		sys.exit(0)

# Run the stargate application
app = GateApplication()
app.run()
