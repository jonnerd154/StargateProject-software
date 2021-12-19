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
        self.electronics = app.electronics
        
        self.loadFromConfig(app)

    def loadFromConfig(self, app):
        # Retrieve the Chevron config and initialize the Chevron objects
        self.chevrons = {}
        for key, value in self.cfg.get("chevronMapping").items():
            self.chevrons[int(key)] = Chevron( self.electronics, value['ledPin'], value['motorNumber'], self.audio, self.cfg )

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
                
    def all_lights_on(self):
        for number, chevron in self.chevrons.items():
            chevron.light_on()


class Chevron:
    """
    This is the class to create and control Chevron objects.
    The led_gpio variable is the number for the gpio pin where the led-wire is connected as an int.
    The motor_number is the number for the motor as an int.
    """

    def __init__(self, electronics, led_gpio, motor_number, audio, cfg):

        self.cfg = cfg
        self.audio = audio
        self.electronics = electronics
 
        # Retrieve Configurations
        self.chevronDownAudioHeadStart = self.cfg.get("chevronDownAudioHeadStart") #0.2
        self.chevronDownThrottle = self.cfg.get("chevronDownThrottle") #-0.65 # negative
        self.chevronDownTime = self.cfg.get("chevronDownTime") #0.1
        self.chevronDownWaitTime = self.cfg.get("chevronDownWaitTime") #0.35
        self.chevronUpThrottle = self.cfg.get("chevronUpThrottle") #0.65 # positive
        self.chevronUpTime = self.cfg.get("chevronUpTime") #0.2       

        self.motor_number = motor_number
        self.motor = self.electronics.get_chevron_motor(self.motor_number)

        self.led_gpio = led_gpio
        self.led = self.electronics.get_led(self.led_gpio)
            
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
        self.light_on()
        sleep(self.chevronDownWaitTime) # wait time without motion

    def up(self):
        ### Chevron Down ###
        self.audio.sound_start('chevron_2') # chev up audio
        self.motor.throttle = self.chevronUpThrottle # Start the motor
        sleep(self.chevronUpTime) # motor movement time
        self.motor.throttle = None # Stop the motor

    def light_on(self):
        if self.led:
            self.led.on()
    
    def incoming_on(self):
        if self.led:
            self.led.on()
        
        self.audio.play_random_clip_from_group("incoming_chevron_sounds", True)

    def off(self, sound=None):
        if sound == 'on':
            choice(self.audio.incoming_chevron_sounds).play()
        if self.led:
            self.led.off()
