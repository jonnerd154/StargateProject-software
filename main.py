#!/usr/bin/python3
# pylint: disable=wrong-import-position

"""
This is the stargate program for running the stargate from https://thestargateproject.com
This main.py file is run automatically on boot. It is executed in the .bashrc file for the sg1 user.
"""

import sys
import os
from http.server import HTTPServer
import threading
import atexit
import schedule

# Include the classes shared between galaxy variants
sys.path.append('classes')
sys.path.append('config')

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio
from web_server import StargateWebServer

#GALAXY = "Milky Way"
GALAXY = "Pegasus"

# Include the galaxy-specific variants
if GALAXY == "Milky Way":
    sys.path.append('classes/StargateMilkyWay')
elif GALAXY == "Pegasus":
    sys.path.append('classes/StargatePegasus')

from stargate import Stargate
from electronics import Electronics
from network_tools import NetworkTools

class GateApplication:

    def __init__(self):

        self.galaxy = GALAXY

        # Check that we're running with root-like permissions (sudo)
        if not os.geteuid() == 0:
            print("The Stargate software must run with root-like permissions (use sudo)")
            print("Stopping startup.")
            sys.exit(1)

        # Check if we're running in systemd, some functionality will change if so.
        self.is_daemon = self.check_is_daemon()

        # Get the base path of execution - this is used in various places when working with files
        self.base_path = os.path.split(os.path.abspath(__file__))[0]

        ### Load our config file.
        self.cfg = StargateConfig(self.base_path, "config", self.galaxy)

        ### Setup the logger. If we're in systemd, don't print to the console.
        self.log = AncientsLogBook(self.base_path, "sg1.log", print_to_console = not self.is_daemon )
        self.cfg.set_log(self.log)
        self.cfg.load()

        ### Start the websockets-based LogTailServer
        # from websocket_server import LogTailServerWrapper
        # self.log_tail_server = LogTailServerWrapper("logs/sg1.log", str(9000))
        # self.log_tail_server.start()

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
        self.log.log('')
        self.log.log(f'Running as Daemon: {self.is_daemon}')

        ### Detect our electronics and initialize the hardware
        self.electronics = Electronics(self)

        ### Initialize the Audio class and do some setup
        self.audio = StargateAudio(self, self.base_path)

        ### We'll use NetworkTools and Schedule throughout the app, initialize them here.
        self.net_tools = NetworkTools(self.log)
        self.schedule = schedule # Alias the class here so it can be used in with a clear interface

        ### Check for new software updates ###
        self.sw_updater = SoftwareUpdate(self)
        if self.cfg.get("software_update_enabled"):
            self.sw_updater.check_and_install()

        ### Create the Stargate object
        self.log.log(f'Booting up the Stargate! Version {self.sw_updater.get_current_version()}')

        # Actually start it...
        self.stargate = Stargate(self)

        ### Start the web server
        try:
            StargateWebServer.stargate = self.stargate
            self.httpd_server = HTTPServer(('', self.cfg.get("control_api_server_port")), StargateWebServer)
            self.httpd_thread = threading.Thread(name="stargate-http", target=self.httpd_server.serve_forever)
            self.httpd_thread.daemon = True
            self.httpd_thread.start()
            self.log.log(f'Web Services API running on: {self.net_tools.get_local_ip()}:{self.cfg.get("control_api_server_port")}')
        except:
            self.log.log("Failed to start webserver. Is the port in use?")
            raise

        ### Register atexit handler
        atexit.register(self.cleanup) # Ensure we handle cleanup before quitting, even on exception

    def run(self):
        self.stargate.update() #This will keep running as long as `stargate.running` is True.

    def cleanup(self):
        self.stargate.ring.release()      # Release the ring when exiting. Just in case.
        self.httpd_server.shutdown()
        #self.log_tail_server.terminate()

        self.log.log('The Stargate program is no longer running\r\n\r\n')
        sys.exit(0)

    @staticmethod
    def check_is_daemon():
        for index, arg in enumerate(sys.argv): # pylint: disable=unused-variable
            if arg == '--daemon':
                return True
        return False

# Run the stargate application
app = GateApplication()
app.run()
