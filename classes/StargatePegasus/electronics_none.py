from hardware_simulation import StepperSim
from hardware_simulation import DCMotorSim
from hardware_simulation import LEDSim
from hardware_simulation import NeopixelSim

class ElectronicsNone:

    def __init__(self):

        self.name = "Impaired - NeoPixel, Relay or other Hardware"

    def init_led_driver(self):
        # Initialize the LED Driver
        self.neopixel_chain = NeopixelSim()
