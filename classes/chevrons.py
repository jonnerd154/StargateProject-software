from random import choice
import simpleaudio as sound
from time import sleep

from hardware_detection import HardwareDetector

# You can change or the values in this file to match your setup. This file should not be overwritten with an automatic update
# The first number in the parenthesis is the gpio led number and the second value is the motor number.

class ChevronManager:

    def __init__(self, app):

        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio

        self.loadFromConfig()

    def loadFromConfig(self, app):
        # Detect the connected Motor Hardware
        hwDetector = HardwareDetector()
        self.motorHardwareMode = hwDetector.getMotorHardwareMode()

        # Retrieve the Chevron config and initialize the Chevron objects
        self.chevrons = {}
        for key, value in self.cfg.get("chevronMapping").items():
            self.chevrons[int(key)] = Chevron( app.electronics, value['ledPin'], value['motorNumber'], self.motorHardwareMode, self.audio )

    def get( self, chevronNumber ):
        return self.chevrons[int(chevronNumber)]

    def all_off(self, sound=None):
        """
        A helper method to turn off all the chevrons
        :param sound: Set sound to 'on' if sound is desired when turning off a chevron light.
        :param chevrons: the dictionary of chevrons
        :return: Nothing is returned
        """
        for number, chevron in self.chevrons.items():
            if sound == 'on':
                chevron.off(sound='on')
            else:
                chevron.off()


class Chevron:
    """
    This is the class to create and control Chevron objects.
    The led_gpio variable is the number for the gpio pin where the led-wire is connected as an int.
    The motor_number is the number for the motor as an int.
    """

    def __init__(self, electronics, led_gpio, motor_number, motorHardwareMode, audio):

        self.audio = audio
        self.enableMotors = False # TODO: Move to cfg
        self.enableLights = False # TODO: Move to cfg

        self.chevronDownAudioHeadStart = 0.2
        self.chevronDownThrottle = -0.65 # negative
        self.chevronDownTime = 0.1
        self.chevronDownWaitTime = 0.35

        self.chevronUpThrottle = -0.65 # positive
        self.chevronUpTime = 0.2

        self.motor_number = motor_number
        self.motorHardwareMode = motorHardwareMode
        self.motor = electronics.get_chevron_motor(self.motor_number)

        self.led_gpio = led_gpio
        self.led = self.get_led_driver()

    def get_led_driver(self):
        if self.enableLights: # TODO: Add hardware detection
            #if self.motorHardwareMode == 1:
                from gpiozero import LED

                if self.led_gpio is not None:
                    return LED(self.led_gpio)
                else:
                    from hardware_simulation import GPIOSim # TODO: when hardware detection is added this can be removed
                    return GPIOSim()

            ### put other LED driver options here

        else:
            from hardware_simulation import GPIOSim
            return GPIOSim()

    def cycle_outgoing(self):
        self.down() # Motor down, light on
        self.up() # Motor up, light unchanged

    def down(self):
        ### Chevron Down ###
        self.audio.sound_start('chevron_1') # chev down audio
        sleep(self.chevronDownAudioHeadStart)

        self.motor.throttle = self.chevronDownThrottle # Start the motor
        sleep(self.chevronDownTime) # Motor movement time
        self.motor.throttle = None # Stop the motor

        ### Turn on the LED ###
        sleep(self.chevronDownWaitTime) # wait time without motion
        self.audio.sound_start('chevron_3') # led on audio
        if self.led:
            self.led.on()
        sleep(self.chevronDownWaitTime) # wait time without motion

    def up(self):
        ### Chevron Down ###
        self.audio.sound_start('chevron_2') # chev up audio
        self.motor.throttle = self.chevronUpThrottle # Start the motor
        sleep(self.chevronUpTime) # motor movement time
        self.motor.throttle = None # Stop the motor

    def incoming_on(self):
        if self.led:
            self.led.on()
        choice(self.audio.incoming_chevron_sounds).play().wait_done()  # random led on audio

    def off(self, sound=None):
        if sound == 'on':
            choice(self.audio.incoming_chevron_sounds).play()  # random led on audio
        if self.led:
            self.led.off()
