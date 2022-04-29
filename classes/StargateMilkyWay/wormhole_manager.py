from time import sleep, time
from datetime import timedelta
from pathlib import Path
import math

from wormhole_animation_manager import WormholeAnimationManager

class WormholeManager:
    """
    This class handles all things wormhole. It takes the stargate object as input.
    """
    def __init__(self, stargate):

        # For convenience
        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.app.audio
        self.electronics = stargate.electronics

        # Initialize the NeoPixel strip and the WormholePatternManager
        self.pixels = self.electronics.get_wormhole_pixels()
        self.tot_leds = self.electronics.get_wormhole_pixel_count()
        self.animation_manager = WormholeAnimationManager(stargate)

        self.root_path = Path(__file__).parent.absolute()

        # Retrieve the configurations
        self.wormhole_max_time_default = self.cfg.get("wormhole_max_time_minutes") * 60  # A wormhole can only be maintained for about 38 minutes without tremendous amounts of power. (Black hole)
        self.wormhole_max_time_blackhole = self.cfg.get("wormhole_max_time_blackhole") * 60   # Make it 10 years...
        self.audio_play_random_clips = self.cfg.get("audio_play_random_clips")  # True to play random clips while WH established
        self.audio_clip_wait_time_default = self.cfg.get("audio_wormhole_active_quotes_interval")  # The frequency of the random audio clips.
        self.audio_clip_wait_time_blackhole = self.cfg.get("audio_clip_wait_time_blackhole")
        self.audio_wormhole_close_headstart = self.cfg.get("audio_wormhole_close_headstart") # How early should we start playing the "wormhole close" sound clip before running the hardware close procedure

        # Load some state variables
        self.audio_clip_wait_time = self.audio_clip_wait_time_default
        self.wormhole_max_time = self.wormhole_max_time_default

        self.open_time = None

    def initialize_animation_manager(self):
        self.animation_manager.after_init(self)

    def open_wormhole(self):
        """
        Method for opening the wormhole. For some reason i did not use the fade_transition function here..
        :return: Nothing is returned.
        """
        self.audio.sound_start('wormhole_open')  # Open wormhole audio
        self.animation_manager.animate_kawoosh()

    def close_wormhole(self):
        """
        Method to disengage the wormhole
        :return: Nothing is returned
        """

        def pattern_blue(number_of_leds):
            blue_pattern = []
            for index in range(number_of_leds): # pylint: disable=unused-variable
                blue_pattern.append((81, 110, 158))
            return blue_pattern

        no_pattern = self.animation_manager.pattern_manager.pattern_off()

        self.stargate.wormhole_active = True  # temporarily to be able to use the fade_transition function
        self.animation_manager.fade_transition(pattern_blue(self.tot_leds))
        self.audio.sound_start('wormhole_close')  # Play the close wormhole audio
        sleep(self.audio_wormhole_close_headstart)
        self.animation_manager.fade_transition(no_pattern)

        # Reset some state variables
        self.stargate.wormhole_max_time = self.wormhole_max_time_default # Reset the variable
        self.stargate.audio_clip_wait_time = self.audio_clip_wait_time_default # Reset the variable
        self.stargate.wormhole_active = False  # Put it back the way it should be.

    def get_time_remaining(self):
        if self.open_time:
            time_elapsed = time() - self.open_time
            return math.floor(self.wormhole_max_time - time_elapsed)
        return 0

    def establish_wormhole(self):
        """
        This is the main method in the wormhole class that opens and maintains a wormhole
        :return: Nothing is returned.
        """

        # Open The wormhole
        self.log.log('Opening Wormhole!')
        self.open_wormhole()

        # this will play the worm hole active audio. It lasts about 4min 22sec. It is deliberately not looping or restarting.
        self.audio.sound_start('wormhole_established')

        self.open_time = time()
        random_audio_start_time = self.open_time

        # Assume we did not dial a black hole
        audio_group = "audio_clips"

        # If we dialed the black hole planet, change some variables
        if self.stargate.black_hole:  # If we dialed the black hole.
            self.wormhole_max_time = self.wormhole_max_time_blackhole * 60  # Make it 10 years...
            self.audio_clip_wait_time = self.audio_clip_wait_time_blackhole
            audio_group = "audio_clips/black_hole"

        # Keep the wormhole open
        while self.stargate.wormhole_active and self.get_time_remaining() > 0:  # as long as stargate.wormhole_active, but for less time than the wormhole_max_time.

            # TODO: These take a long time, and as a result we don't have tight timing
            # on wormhole close/timeout, and the random clips.
            #    Maybe the Neopixel stuff should run in it's own thread?

            # Change the patterns/animations around with transitions
            self.animation_manager.do_random_transitions(self.stargate.black_hole)

            # Play random audio clips if wormhole not closing
            if self.audio_play_random_clips and self.stargate.wormhole_active and (time() - random_audio_start_time) > self.audio_clip_wait_time:  # If there has been "silence" for more than audio_clip_wait_time
                self.audio.play_random_clip(audio_group) # Won't play if a clip is already playing
                random_audio_start_time = time()

        # Wormhole is closing. Did it close because it ran out of power/time?
        if self.get_time_remaining() < 1:  # if the wormhole closes due to the 38min time limit.
            if self.audio.random_clip_is_playing():  # If the random audio clip is still playing:
                self.audio.random_clip_wait_done()  # wait until it's finished.

            self.audio.play_random_clip("38min")  # The 38min ones.
            self.audio.random_clip_wait_done()  # wait until it's finished.

        self.close_wormhole()
        if self.audio.is_playing('wormhole_established'):
            self.audio.sound_stop('wormhole_established')
        self.stargate.wormhole_active = False # The close_wormhole method also does this.. shouldn't be needed.
        self.log.log(f'Disengaged Wormhole after {timedelta(seconds=int(time() - self.open_time))}')
        self.open_time = None
