from adafruit_motorkit import MotorKit # pylint: disable=import-error
from adafruit_motor import stepper as stp
import spidev # pylint: disable=import-error
import neopixel # pylint: disable=import-error
import board # pylint: disable=import-error
from gpiozero import LED # pylint: disable=import-error

from hardware_simulation import DCMotorSim, StepperSim

class ElectronicsOriginal:

    def __init__(self, app):

        self.cfg = app.cfg

        self.name = "Kristian's Original 3-Shield Stack w/Optional Homing"

        self.stepper_motor_enable = self.cfg.get("stepper_motor_enable")
        self.chevron_motors_enable = self.cfg.get("chevron_motors_enable")

        self.motor_shield_address_1 = 0x60
        self.motor_shield_address_2 = 0x61
        self.motor_shield_address_3 = 0x62

        self.neopixel_pin = board.D12
        self.neopixel_led_count = 122

        self.adc_resolution = 10 # The MCP3002 is a 10-bit ADC
        self.adc_vref = 3.3
        self.spi_bit_rate = 1200000
        self.spi_ch = 1

    # ------------------------------------------

        self.shield_config = None
        self.stepper = None

        self.init_motor_shields()

        self.drive_modes = {
            "double": stp.DOUBLE,
            "single": stp.SINGLE,
            "interleave": stp.INTERLEAVE,
            "microstep": stp.MICROSTEP
        }

        self.neopixels = None
        self.init_neopixels()

        self.spi = None
        self.init_spi_for_adc()

    def init_motor_shields(self):
        # Initialize all of the shields as DC motors

        if self.chevron_motors_enable:
            self.shield_config =  {
            #1: MotorKit(address=self.motor_shield_address_1).motor1, # Used for Stepper
            #2: MotorKit(address=self.motor_shield_address_1).motor2, # Used for Stepper
            3: MotorKit(address=self.motor_shield_address_1).motor3,
            4: MotorKit(address=self.motor_shield_address_1).motor4,
            5: MotorKit(address=self.motor_shield_address_2).motor1,
            6: MotorKit(address=self.motor_shield_address_2).motor2,
            7: MotorKit(address=self.motor_shield_address_2).motor3,
            8: MotorKit(address=self.motor_shield_address_2).motor4,
            9: MotorKit(address=self.motor_shield_address_3).motor1,
            10: MotorKit(address=self.motor_shield_address_3).motor2,
            11: MotorKit(address=self.motor_shield_address_3).motor3,
            12: MotorKit(address=self.motor_shield_address_3).motor4
        }
        else:
            self.shield_config =  {
            3: DCMotorSim(),
            4: DCMotorSim(),
            5: DCMotorSim(),
            6: DCMotorSim(),
            7: DCMotorSim(),
            8: DCMotorSim(),
            9: DCMotorSim(),
            10: DCMotorSim(),
            11: DCMotorSim(),
            12: DCMotorSim(),
        }
        # Initialize the Stepper
        if self.stepper_motor_enable:
            self.stepper = MotorKit(address=self.motor_shield_address_1).stepper1
        else:
            self.stepper = StepperSim()

    def get_chevron_motor(self, chevron_number):
        return self.shield_config[chevron_number]

    def get_stepper(self):
        return self.stepper

    @staticmethod
    def get_stepper_forward():
        return stp.FORWARD

    @staticmethod
    def get_stepper_backward():
        return stp.BACKWARD

    def get_stepper_drive_mode(self, drive_mode):
        try:
            return self.drive_modes[drive_mode]
        except KeyError:
            #self.log.log("Unsupported Stepper Drive Mode: {}. Using 'double'".format(drive_mode))
            return self.drive_modes['double']

    def init_spi_for_adc(self):
        # Initialize the SPI hardware to talk to the external ADC

        # Make sure you've enabled the Raspi's SPI peripheral: `sudo raspi-config`
        self.spi = spidev.SpiDev(0, self.spi_ch)
        self.spi.max_speed_hz = self.spi_bit_rate

    def get_adc_by_channel(self, adc_ch):
        # CREDIT: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

        # Make sure ADC channel is 0 or 1
        if adc_ch not in [0,1]:
            raise ValueError

        # Construct SPI message
        msg = 0b11 # Start bit
        msg = ((msg << 1) + adc_ch) << 5 # Select channel, read in non-differential mode
        msg = [msg, 0b00000000] # clock the response back from ADC, 12 bits
        reply = self.spi.xfer2(msg) # read the response and store it in a variable

        # Construct single integer out of the reply (2 bytes)
        adc_value = 0
        for byte in reply:
            adc_value = (adc_value << 8) + byte

        # Last bit (0) is not part of ADC value, shift to remove it
        adc_value = adc_value >> 1

        return adc_value

    def adc_to_voltage( self, adc_value ):
        # Convert ADC value to voltage
        return (self.adc_vref * adc_value) / (2^self.adc_resolution)-1

    def homing_supported(self):
        # Tie ADC CH1 HIGH to enable homing
        if 0.000 < self.adc_to_voltage( self.get_adc_by_channel(1) ) < 1:
            return True
        return False

    def get_homing_sensor_voltage(self):
        return self.adc_to_voltage( self.get_adc_by_channel(0) )

    def init_neopixels(self):
        self.neopixels = neopixel.NeoPixel(self.neopixel_pin, self.neopixel_led_count, auto_write=False, brightness=0.61)

    def get_wormhole_pixels(self):
        return self.neopixels

    def get_wormhole_pixel_count(self):
        return self.neopixel_led_count

    @staticmethod
    def get_led(gpio_number):
        if gpio_number:
            return LED(gpio_number)
        return None
