from time import sleep

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

# -------------------------------------------------------

class StepperSim:

    def __init__(self):

        self.onestepTime = 0.0038 # in seconds, how long does a step take to exec on real HW
        pass

    def onestep(self, direction, style):
        sleep(self.onestepTime)
        pass

    def release(self):
        pass

class DCMotorSim:

    def __init__(self):
        self.throttle = 0
        pass

    def onestep(self, direction, style):
        pass

    def release(self):
        pass


class LEDSim:
    def __init__(self):
        pass

    def on(self):
        pass

    def off(self):
        pass

class NeopixelSim:

	def __init__(self):
		pass

	def show(self):
		pass

	def fill(self, color_tuple):
		pass

	def __setitem__(self, index, val):
		return None

	def __getitem__(self, index):
		return [ [], [], [] ]
