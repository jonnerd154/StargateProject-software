from random import choice
from time import sleep

class ChevronManager:

    def __init__(self, app):

        self.log = app.log
        self.cfg = app.cfg
        self.audio = app.audio
        self.electronics = app.electronics

        self.chevrons = {}
        self.load_from_config()

    def load_from_config(self):
        # Retrieve the Chevron config and initialize the Chevron objects
        self.chevrons = {}
        for index in range(1,10):
            self.chevrons[index] = Chevron( self.electronics, self.audio, self.cfg )

    def get( self, chevron_number ):
        return self.chevrons[int(chevron_number)]

    def get_status( self ):
        output = {}
        for index, chevron in self.chevrons.items():
            row = {}
            row['led_state'] = chevron.led_state
            output[index] = row
        return output

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

    def __init__(self, electronics, audio, cfg):

        self.cfg = cfg
        self.audio = audio
        self.electronics = electronics

        # Retrieve Configurations
        # TODO: Move to allow config to change without restart
        self.audio_chevron_down_headstart = self.cfg.get("audio_chevron_down_headstart") #0.2
        self.chevron_down_wait_time = self.cfg.get("chevron_down_wait_time") #0.35

        self.led_state = False

    def lock(self):
        self.audio.sound_start('chevron_lock') # chev down audio
        sleep(self.audio_chevron_down_headstart)
        self.light_on()

    def light_on(self):
        if self.led:
            self.led.on()
        self.led_state = True

    def incoming_on(self):
        if self.led:
            self.led.on()

        self.audio.incoming_chevron()

    def off(self, sound=None):
        if sound == 'on':
            choice(self.audio.incoming_chevron_sounds).play()
        if self.led:
            self.led.off()
        self.led_state = False