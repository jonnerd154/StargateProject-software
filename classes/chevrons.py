from random import choice
from time import sleep

class ChevronManager:

    def __init__(self, app):

        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio
        self.electronics = app.electronics

        self.load_from_config()

    def load_from_config(self):
        # Retrieve the Chevron config and initialize the Chevron objects
        self.chevrons = {}
        for key, value in self.cfg.get("chevronMapping").items():
            self.chevrons[int(key)] = Chevron( self.electronics, value['ledPin'], value['motorNumber'], self.audio, self.cfg )

    def get( self, chevron_number ):
        return self.chevrons[int(chevron_number)]

    def all_off(self, sound_on=None):
        """
        A helper method to turn off all the chevrons
        :param sound_on: Set sound_on to 'on' if sound is desired when turning off a chevron light.
        :param chevrons: the dictionary of chevrons
        :return: Nothing is returned
        """
        for chevron in self.chevrons.values():
            if sound_on == 'on':
                chevron.off(sound_on='on')
            else:
                chevron.off()

    def all_lights_on(self):
        for chevron in self.chevrons.values():
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
        self.chevron_down_audio_head_start = self.cfg.get("chevronDownAudioHeadStart") #0.2
        self.chevron_down_throttle = self.cfg.get("chevronDownThrottle") #-0.65 # negative
        self.chevron_down_time = self.cfg.get("chevronDownTime") #0.1
        self.chevron_down_wait_time = self.cfg.get("chevronDownWaitTime") #0.35
        self.chevron_up_throttle = self.cfg.get("chevronUpThrottle") #0.65 # positive
        self.chevron_up_time = self.cfg.get("chevronUpTime") #0.2

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
        sleep(self.chevron_down_audio_head_start)

        self.motor.throttle = self.chevron_down_throttle # Start the motor
        sleep(self.chevron_down_time) # Motor movement time
        self.motor.throttle = None # Stop the motor

        ### Turn on the LED ###
        sleep(self.chevron_down_wait_time) # wait time without motion
        self.audio.sound_start('chevron_3') # led on audio
        self.light_on()
        sleep(self.chevron_down_wait_time) # wait time without motion

    #TODO: Consider renaming
    def up(self): # pylint: disable=invalid-name
        ### Chevron Down ###
        self.audio.sound_start('chevron_2') # chev up audio
        self.motor.throttle = self.chevron_up_throttle # Start the motor
        sleep(self.chevron_up_time) # motor movement time
        self.motor.throttle = None # Stop the motor

    def light_on(self):
        if self.led:
            self.led.on()

    def incoming_on(self):
        if self.led:
            self.led.on()

        self.audio.incoming_chevron()

    def off(self, sound=None):
        if sound == 'on':
            choice(self.audio.incoming_chevron_sounds).play()
        if self.led:
            self.led.off()
