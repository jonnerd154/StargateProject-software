from adafruit_motorkit import MotorKit
from adafruit_motor import stepper as stp
import spidev
import neopixel, board
from gpiozero import LED

from hardware_simulation import DCMotorSim, StepperSim

class ElectronicsOriginal:

    def __init__(self, app):
        
        self.enableStepperMotor = True
        self.enableChevronMotors = True

        self.motorShield1Address = 0x60
        self.motorShield2Address = 0x61
        self.motorShield3Address = 0x62

        self.neopixelPin = board.D12
        self.neopixelLEDCount = 122

        self.adc_resolution = 10 # The MCP3002 is a 10-bit ADC
        self.adc_vref = 3.3

    # ------------------------------------------

        self.shieldConfig = None
        self.stepper = None
        self.init_motor_shields()

        self.driveModes = {
            "double": stp.DOUBLE,
            "single": stp.SINGLE,
            "interleave": stp.INTERLEAVE,
            "microstep": stp.MICROSTEP
        }

        self.neopixels = None
        self.init_neopixels()

    def init_motor_shields(self):
        # Initialize all of the shields as DC motors
        
        if self.enableChevronMotors:
            self.shieldConfig =  {
            #1: MotorKit(address=self.motorShield1Address).motor1, # Used for Stepper
            #2: MotorKit(address=self.motorShield1Address).motor2, # Used for Stepper
            3: MotorKit(address=self.motorShield1Address).motor3,
            4: MotorKit(address=self.motorShield1Address).motor4,
            5: MotorKit(address=self.motorShield2Address).motor1,
            6: MotorKit(address=self.motorShield2Address).motor2,
            7: MotorKit(address=self.motorShield2Address).motor3,
            8: MotorKit(address=self.motorShield2Address).motor4,
            9: MotorKit(address=self.motorShield3Address).motor1,
            10: MotorKit(address=self.motorShield3Address).motor2,
            11: MotorKit(address=self.motorShield3Address).motor3,
            12: MotorKit(address=self.motorShield3Address).motor4
        }
        else:
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
            12: DCMotorSim(),
        }
        # Initialize the Stepper
        if self.enableStepperMotor:
            self.stepper = MotorKit(address=self.motorShield1Address).stepper1
        else:
            self.stepper = StepperSim()
            
        

    def get_chevron_motor(self, chevron_number):
        return self.shieldConfig[chevron_number]

    def get_stepper(self):
        return self.stepper

    def get_stepper_forward(self):
        return stp.FORWARD

    def get_stepper_backward(self):
        return stp.BACKWARD

    def get_stepper_drive_mode(self, driveMode):
        try:
            return self.driveModes[driveMode]
        except KeyError:
            self.log.log("Unsupported Stepper Drive Mode: {}. Using 'double'".format(driveMode))
            return self.driveModes['double']

    def init_spi_for_adc():
        # Initialize the SPI hardware to talk to the external ADC

        # Make sure you've enabled the Raspi's SPI peripheral: `sudo raspi-config`
        self.spi = spidev.SpiDev(0, self.spi_ch)
        self.spi.max_speed_hz = 1200000

    def get_adc_by_channel(adc_ch):
        # CREDIT: https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

        self.init_spi_for_adc()

        # Make sure ADC channel is 0 or 1
        if adc_ch not in [0,1]:
            raise ValueError

        # Construct SPI message
        msg = 0b11 # Start bit
        msg = ((msg << 1) + adc_ch) << 5 # Select channel, read in non-differential mode
        msg = [msg, 0b00000000] # clock the response back from ADC, 12 bits
        reply = spi.xfer2(msg) # read the response and store it in a variable

        # Construct single integer out of the reply (2 bytes)
        adc_value = 0
        for byte in reply:
            adc_value = (adc_value << 8) + byte

        # Last bit (0) is not part of ADC value, shift to remove it
        adc_value = adc_value >> 1

        return adc_value

    def adc_to_voltage( self, adc_value ):
        # Convert ADC value to voltage
        return (self.adc_vref * adc_value) / (2^self.adc_resolution) #TODO: This should be minus one

    def homing_enabled(self):
        if 0.000 < self.adc_to_voltage( self.get_adc_by_channel(1) ) < 1:
            return True
        return False

    def get_homing_sensor_voltage(self):
        return self.adc_to_voltage( self.get_adc_by_channel(0) )

    def init_neopixels(self):
        self.neopixels = neopixel.NeoPixel(self.neopixelPin, self.neopixelLEDCount, auto_write=False, brightness=0.61)

    def get_wormhole_pixels(self):
        return self.neopixels

    def get_wormhole_pixel_count(self):
        return self.neopixelLEDCount

    def get_led(self, gpio_number):
        if gpio_number:
            return LED(gpio_number)
        else:
            return None