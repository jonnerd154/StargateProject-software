from led_driver import LEDDriver

class ElectronicsMainBoard:

    def __init__(self, app):

        self.cfg = app.cfg
        self.log = app.log

        self.name = "Stargate Pegasus Main Board"

        self.led_driver = PegasusLEDDriver( self.cfg, self.log ):
