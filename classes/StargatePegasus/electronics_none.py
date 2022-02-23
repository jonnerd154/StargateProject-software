from hardware_simulation import StepperSim
from hardware_simulation import DCMotorSim
from hardware_simulation import LEDSim
from hardware_simulation import NeopixelSim

class ElectronicsNone:

    def __init__(self, log):

        self.name = "Impaired - NeoPixel, Relay or other Hardware"

        self.led_driver = LEDDriverSim(log)
