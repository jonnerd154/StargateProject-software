from hardware_simulation import DCMotorSim, StepperSim, NeopixelSim, LEDSim

class ElectronicsNone:

    def __init__(self, app):

        self.neopixelPin = None
        self.neopixelLEDCount = 122 # must be non-zero

        self.adc_resolution = None
        self.adc_vref = None

    # ------------------------------------------

        self.shieldConfig = None
        self.stepper = None
        self.init_motor_shields()

        self.driveModes = {}

        self.neopixels = None
        self.init_neopixels()

    def init_motor_shields(self):
        # Initialize all of the shields as DC motors
        self.shieldConfig =  {
            3: DCMotorSim(),
            4: DCMotorSim(),
            5: DCMotorSim(),
            6: DCMotorSim(),
            7: DCMotorSim(),
            8: DCMotorSim(),
            9: DCMotorSim(),
            10: DCMotorSim(),
            11: DCMotorSim(),
            12: DCMotorSim()
        }

        # Initialize the Stepper
        self.stepper = StepperSim()

    def get_chevron_motor(self, chevron_number):
        return self.shieldConfig[chevron_number]

    def get_stepper(self):
        return self.stepper

    def get_stepper_forward(self):
        return 0

    def get_stepper_backward(self):
        return 0

    def get_stepper_drive_mode(self, driveMode):
        return 0

    def init_spi_for_adc():
        pass

    def get_adc_by_channel(adc_ch):
        return 0

    def homing_enabled(self):
        return False

    def get_homing_sensor_voltage(self):
        return 0

    def init_neopixels(self):
        self.neopixels = NeopixelSim()

    def get_wormhole_pixels(self):
        return self.neopixels

    def get_wormhole_pixel_count(self):
        return self.neopixelLEDCount

    def get_led(self, gpio_number):
        return LEDSim()
