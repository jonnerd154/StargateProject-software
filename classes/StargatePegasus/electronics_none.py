from hardware_simulation import LEDDriverSim

class ElectronicsNone:

    def __init__(self, log):

        self.name = "Impaired - NeoPixel, Relay or other Hardware MISSING"

        self.led_driver = LEDDriverSim(log)

        self.gpio_pins = {}
        self.serial_to_driver = None
        
