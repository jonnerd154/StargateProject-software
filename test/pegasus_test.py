import sys
import os
from time import sleep

sys.path.append('classes')
from ancients_log_book import AncientsLogBook
from stargate_config import StargateConfig

sys.path.append('classes/StargatePegasus')
from electronics import Electronics
from chevrons import ChevronManager
from stargate_audio import StargateAudio

# Make a bare bones alternative to GateApplication
class Area51App():

    def __init__(self):

        self.is_daemon = False
        self.galaxy = "Pegasus"
        self.galaxy_path = self.galaxy.replace(" ", "").lower()

        # Get the base path of execution - this is used in various places when working with files
        self.base_path = "/Users/jmoyes/Documents/GitHub/StargateProject2021" #os.path.split(os.path.abspath(__file__))[0]

        ### Load our config file.
        self.cfg = StargateConfig(self.base_path, "config", self.galaxy_path)

        ### Setup the logger. If we're in systemd, don't print to the console.
        self.log = AncientsLogBook(self.base_path, self.galaxy_path + ".log", print_to_console = not self.is_daemon )
        self.cfg.set_log(self.log)
        self.cfg.load()

        self.audio = StargateAudio(self, self.base_path)
        self.electronics = Electronics(self)
        self.stargate = Area51Stargate(self)

    def test(self):

        # Expected behavior:
        #  - All Chevrons on, wait 1 second
        #  - Show symbol 0 in position 0, wait 1 second
        #  - All LEDs off

        # We'll use the Chevrons class because it is fully implemented :tada:
        self.stargate.chevrons.all_lights_on()
        sleep(1)

        # We'd normally (and in the long run) want to use the SymbolRing class,
        #   rather than touching electronics/LedDriver directly.
        #   But! The purpose of this file is to help you develop the SymbolRing class, so
        #   that's okay. Whatever you write in here should eventually get moved into SymbolRing,
        #   Trying to keep everything else (specifically the logic in the Stargate class) exactly
        #   as it is.
        self.electronics.led_driver.display_symbol_in_position ( 0, 0, 0, 255, 0 )
        sleep(1)

        self.electronics.led_driver.clear_all()
        sleep(1)


# !!!!!!!!!!!  No need to edit below! !!!!!!!!!!!!


# Make a bare bones alternative to Stargate to contain ChevronManager instance
class Area51Stargate():

    def __init__(self, app):
        self.cfg = app.cfg
        self.log = app.log
        self.audio = app.audio
        self.electronics = app.electronics
        self.chevrons = ChevronManager(self)

# Run the App
app = Area51App()
app.test()
