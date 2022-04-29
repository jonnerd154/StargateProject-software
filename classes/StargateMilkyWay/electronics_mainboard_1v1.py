from typing import Tuple

import spidev # pylint: disable=import-error
import neopixel # pylint: disable=import-error
import board # pylint: disable=import-error
from gpiozero import LED # pylint: disable=import-error
#from busio import I2C

from adafruit_motor import stepper as stp
import adafruit_motor.motor
from adafruit_pca9685 import PCA9685

from hardware_simulation import DCMotorSim, StepperSim

# pylint: disable=too-many-public-methods

class ElectronicsMainBoard1V1:

    def __init__(self, app):

        self.cfg = app.cfg

        self.name = "Milky Way Main Board v1.1"

        self.stepper_motor_enable = self.cfg.get("stepper_motor_enable")
        self.chevron_motors_enable = self.cfg.get("chevron_motors_enable")

        # Configuration
        self._pca_1_addr = 0x66
        self._pca_2_addr = 0x6F
        self._pwm_frequency = 1600.0
        self._stepper_microsteps = 16

        self.neopixel_pin = board.D12
        self.neopixel_led_count = 122

        self.adc_resolution = 10 # The MCP3002 is a 10-bit ADC
        self.adc_vref = 3.3
        self.spi_bit_rate = 1200000
        self.spi_ch = 1

        self.aux_1_pin = 17
        self.calibration_led_pin = 24
        self.adc_cs_pin = 8

    # ------------------------------------------
        self._pca_1 = None
        self._pca_2 = None
        self.chevron_config = None
        self.stepper1 = None

        # Initialize i2c & the motor control hardware
        self.i2c = board.I2C()
        self.init_motor_hardware()

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

    def init_motor_hardware(self):

        # Initialize the PWM controllers
        self._pca_1 = PCA9685(self.i2c, self._pca_1_addr)
        self._pca_1.frequency = self._pwm_frequency

        self._pca_2 = PCA9685(self.i2c, self._pca_2_addr)
        self._pca_2.frequency = self._pwm_frequency

        if self.chevron_motors_enable:
            self.chevron_config =  {
                3: self.motor1,
                4: self.motor2,
                5: self.motor3,
                6: self.motor4,
                7: self.motor5,
                8: self.motor6,
                9: self.motor7,
                10: DCMotorSim(),
                11: DCMotorSim(),
                12: DCMotorSim(),
            }
        else:
            self.chevron_config =  {
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
            self.stepper1 = self.stepper
        else:
            self.stepper1 = StepperSim()

    def get_chevron_motor(self, chevron_number):
        return self.chevron_config[chevron_number]

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


    def _motor(
        self, controller, motor_name: int, channels: Tuple[int, int, int]
    ) -> adafruit_motor.motor.DCMotor:

        motor_name = "_motor" + str(motor_name)

        controller.channels[channels[0]].duty_cycle = 0xFFFF
        setattr(
            self,
            motor_name,
            adafruit_motor.motor.DCMotor(
                controller.channels[channels[1]], controller.channels[channels[2]]
            ),
        )
        return getattr(self, motor_name)

    @property
    def motor1(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_2, 1, (9, 11, 10)) # Tuple is: [ PWM, IN_POS, IN_NEG ]

    @property
    def motor2(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_2, 2, (6, 8, 7))

    @property
    def motor3(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_2, 3, (3, 5, 4))

    @property
    def motor4(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_2, 4, (0, 2, 1))

    @property
    def motor5(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_1, 4, (12, 14, 13))

    @property
    def motor6(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_1, 4, (5, 3, 4))

    @property
    def motor7(self) -> adafruit_motor.motor.DCMotor:
        return self._motor(self._pca_1, 4, (0, 2, 1))

    @property
    def stepper(self) -> adafruit_motor.stepper.StepperMotor:
        if not self.stepper1:
            self._pca_1.channels[6].duty_cycle = 0xFFFF     # PWMA
            self._pca_1.channels[11].duty_cycle = 0xFFFF    # PWMB
            self.stepper1 = adafruit_motor.stepper.StepperMotor(
                self._pca_1.channels[8],    # AIN1
                self._pca_1.channels[7],    # AIN2
                self._pca_1.channels[9],    # BIN1
                self._pca_1.channels[10],   # BIN2
                microsteps=self._stepper_microsteps,
            )
        return self.stepper1
