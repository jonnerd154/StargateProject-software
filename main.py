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
import schedule

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio
from stargate_sg1 import StargateSG1
from web_server import StargateWebServer
from electronics import Electronics
from network_tools import NetworkTools

class GateApplication:

    def __init__(self):

        dirname, filename = os.path.split(os.path.abspath(__file__))
        self.base_path = dirname

        ### Load our config file
        self.cfg = StargateConfig(self.base_path, "config.json")

        ### Setup the logger
        self.log = AncientsLogBook(self.base_path, "sg1.log")
        self.cfg.set_log(self.log)
        self.cfg.load()

        # Some credits
        self.log.log('*******************************************************************')
        self.log.log("***   Kristian's Stargate Project - TheStargateProject.com      ***".upper())
        self.log.log('*******************************************************************')
        self.log.log("***                                                             ***")
        self.log.log('***   Original Software written by Kristian Tysse               ***')
        self.log.log('***   Restructuring and Development by Jonathan Moyes           ***')
        self.log.log('***   Web Interface adapted from Dan Clarke:                    ***')
        self.log.log('***      https://github.com/danclarke/WorkingStargateMk2Raspi   ***')
        self.log.log("***                                                             ***")
        self.log.log('*******************************************************************\r\n')

        ### Detect our electronics and initialize the hardware
        self.electronics = Electronics(self).hardware

        ### Initialize the Audio class and do some setup
        self.audio = StargateAudio(self, self.base_path)

        ### We'll use NetworkTools and Schedule throughout the app, initialize them here.
        self.netTools = NetworkTools(self.log)
        self.schedule = schedule # Alias the class here so it can be used in with a clear interface

        ### Check for new software updates ###
        self.swUpdater = SoftwareUpdate(self)
        if self.cfg.get("enableUpdates"):
            self.swUpdater.check_and_install()

        ### Create the Stargate object
        self.log.log('Booting up the Stargate! Version {}'.format(self.swUpdater.get_current_version()))

        # Actually start it...
        self.stargate = StargateSG1(self)

        ### Start the web server
        try:
            StargateWebServer.stargate = self.stargate
            self.httpd_server = HTTPServer(('', self.cfg.get("httpServerPort")), StargateWebServer)
            self.httpd_thread = threading.Thread(name="stargate-http", target=self.httpd_server.serve_forever)
            self.httpd_thread.daemon = True
            self.httpd_thread.start()
            self.log.log('Web Services API running on: {}:{}'.format( self.netTools.get_local_ip(), self.cfg.get("httpServerPort") ))

        except:
            raise #self.log.log("Failed to start webserver. Is the port in use?")

        ### Register atexit handler
        atexit.register(self.cleanup) # Ensure we handle cleanup before quitting, even on exception

    def run(self):
        self.stargate.update() #This will keep running as long as `stargate.running` is True.

    def cleanup(self):
        self.stargate.ring.release()      # Release the ring when exiting. Just in case.
        self.httpd_server.shutdown()

        self.log.log('The Stargate program is no longer running\r\n\r\n')
        sys.exit(0)

# Run the stargate application
app = GateApplication()
app.run()
