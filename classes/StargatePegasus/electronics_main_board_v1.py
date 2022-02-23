from led_controller import PegasusLEDController

class ElectronicsMainBoard:

    def __init__(self, app):

        self.cfg = app.cfg
        self.log = app.log

        self.name = "Stargate Pegasus Main Board"

        self.led_controller = PegasusLEDController( self.cfg, self.log ):
