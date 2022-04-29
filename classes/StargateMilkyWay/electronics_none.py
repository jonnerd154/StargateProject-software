from hardware_simulation import StepperSim
from hardware_simulation import DCMotorSim
from hardware_simulation import LEDSim
from hardware_simulation import NeopixelSim

class ElectronicsNone:

    def __init__(self):

        self.name = "Impaired - No Motor, LED, and/or NeoPixel Hardware"

        self.neopixel_pin = None
        self.neopixel_led_count = 122 # must be non-zero

        self.adc_resolution = None
        self.adc_vref = None

    # ------------------------------------------

        self.motor_channels = None
        self.led_channels = None
        self.stepper = None
        self.init_motor_shields()
        self.init_led_gpio()

        self.drive_modes = {}

        self.neopixels = None
        self.init_neopixels()

    def init_motor_shields(self):
        # Initialize all of the shields as DC motors
        self.motor_channels =  {
            1: DCMotorSim(),
            2: DCMotorSim(),
            3: DCMotorSim(),
            4: DCMotorSim(),
            5: DCMotorSim(),
            6: DCMotorSim(),
            7: DCMotorSim(),
            8: DCMotorSim(),
            9: DCMotorSim()
        }

        # Initialize the Stepper
        self.stepper = StepperSim()

    def init_led_gpio(self):
        self.led_channels =  {
            1: LEDSim(),
            2: LEDSim(),
            3: LEDSim(),
            4: LEDSim(),
            5: LEDSim(),
            6: LEDSim(),
            7: LEDSim(),
            8: LEDSim(),
            9: LEDSim()
        }

    def get_chevron_motor(self, chevron_number):
        return self.motor_channels[chevron_number]

    def get_chevron_led(self, chevron_number):
        return self.led_channels[chevron_number]

    def get_stepper(self):
        return self.stepper

    @staticmethod
    def get_stepper_forward():
        return 1 # Forward

    @staticmethod
    def get_stepper_backward():
        return 2 # Backward

    @staticmethod
    def get_stepper_drive_mode(drive_mode): # pylint: disable=unused-argument
        return 2 # Double

    @staticmethod
    def init_spi_for_adc():
        pass

    @staticmethod
    def get_adc_by_channel():
        return 0

    @staticmethod
    def homing_supported():
        return False

    @staticmethod
    def get_homing_sensor_voltage():
        return 0

    def init_neopixels(self):
        self.neopixels = NeopixelSim(self.neopixel_led_count)

    def get_wormhole_pixels(self):
        return self.neopixels

    def get_wormhole_pixel_count(self):
        return self.neopixel_led_count
