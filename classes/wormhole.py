from random import choice, randint
from time import sleep, time
from datetime import timedelta
from pathlib import Path
import math

class Wormhole:
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

        self.pixels = self.electronics.get_wormhole_pixels()
        self.tot_leds = self.electronics.get_wormhole_pixel_count()

        self.root_path = Path(__file__).parent.absolute()

        # Retrieve the configurations
        self.wormhole_max_time_default = self.cfg.get("wormhole_max_time_minutes") * 60  # A wormhole can only be maintained for about 38 minutes without tremendous amounts of power. (Black hole)
        self.wormhole_max_time_blackhole = self.cfg.get("wormhole_max_time_blackhole") * 60   # Make it 10 years...
        self.audio_clip_wait_time_default = self.cfg.get("wormhole_open_random_sound_interval_seconds")  # The frequency of the random audio clips.
        self.audio_clip_wait_time_blackhole = self.cfg.get("audio_clip_wait_time_blackhole")
        self.wormhole_close_audio_headstart = self.cfg.get("wormhole_close_audio_headstart") # How early should we start playing the "wormhole close" sound clip before running the hardware close procedure

        # Load some state variables
        self.audio_clip_wait_time = self.audio_clip_wait_time_default
        self.wormhole_max_time = self.wormhole_max_time_default

        # Turn off all the LEDs
        self.clear_wormhole()

        self.open_time = None

    ## The wormhole helper functions
    def clear_wormhole(self):
        """
        This method simply clears the wormhole or turns off all the leds.
        :return: Nothing is returned.
        """
        pattern = self.pattern_off(self.tot_leds)
        self.set_wormhole_pattern(self.pixels, pattern)

    def possible_wormholes(self, black_hole=False):
        def pattern1(number_of_leds, color1, color2):
            """
            This method creates the wormhole pattern1
            :param number_of_leds: the total number of leds in the led strip
            :param color1: the first color as a tuple of rgb values, eg: (26, 56, 105)
            :param color2: the second color as a tuple of rgb values, eg: (26, 56, 105)
            :return: A list containing the led colors for the wormhole is returned.
            """
            pattern = []
            for led in range(number_of_leds):
                pattern.append(color1)
            for led in range(0, number_of_leds, 5):
                pattern[led] = color2
                pattern[led - 1] = color2
            return pattern

        def pattern2(number_of_leds, base_color, size):
            """
            This method creates the wormhole pattern2
            :param number_of_leds: the total number of leds in the led strip
            :param base_color: The base color for the pattern
            :param size: the size of the spacing in the pattern. Should be an int between 5, and 15 should be fine.
            :return: A list is returned.
            """
            pattern = []
            second_color = ((base_color[0] + 5) % 255, (base_color[1] + 5) % 255, (base_color[2] - 190) % 255)
            third_color = ((base_color[0] + 5) % 255, (base_color[1] + 200) % 255, (base_color[2] // 2) % 255)
            for led in range(number_of_leds):
                pattern.append(base_color)
            for led in range(0, number_of_leds, number_of_leds // size):
                pattern[led] = second_color
                pattern[(led + 1) % number_of_leds] = second_color
                pattern[(led - 1) % number_of_leds] = second_color
                pattern[(led + 2) % number_of_leds] = third_color
                pattern[(led - 2) % number_of_leds] = third_color
            return pattern

        def pattern3(number_of_leds, base_color, size):
            """
            This method creates the wormhole pattern3
            :param number_of_leds: the total number of leds in the led strip
            :param base_color: The base color for the pattern
            :param size: the size of the spacing in the pattern. 10 seems fine.
            :return: A list is returned.
            """
            pattern = []
            for led in range(number_of_leds):
                pattern.append(base_color)
            for led in range(0, number_of_leds, size):
                # pattern[led] = (base_color[0//2], base_color[1]//2, base_color[2]//2)
                pattern[(led - 1) % number_of_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
                pattern[(led - 2) % number_of_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
                pattern[(led - 3) % number_of_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
                pattern[(led - 4) % number_of_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
                pattern[(led - 5) % number_of_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
                pattern[(led - 6) % number_of_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
                pattern[(led - 7) % number_of_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
                pattern[led] = base_color
                pattern[(led + 1) % number_of_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
                pattern[(led + 2) % number_of_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
                pattern[(led + 3) % number_of_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
                pattern[(led + 4) % number_of_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
                pattern[(led + 5) % number_of_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
                pattern[(led + 6) % number_of_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
                pattern[(led + 7) % number_of_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
            return pattern

        ## Set some variables for wormhole manipulations
        if not black_hole:
            pos_patterns = [pattern1(self.tot_leds, (26, 56, 105), (5, 37, 247)),
                            pattern1(self.tot_leds, (2, 172, 207), (5, 46, 250)),
                            pattern1(self.tot_leds, (56, 25, 252), (97, 184, 255)),
                            pattern2(self.tot_leds, (0, 0, 200), 12),
                            pattern2(self.tot_leds, (0, 10, 255), 8),
                            pattern2(self.tot_leds, (10, 20, 200), 15),
                            pattern3(self.tot_leds, (10, 10, 255), 10),
                            pattern3(self.tot_leds, (64, 229, 247), 11),
                            pattern3(self.tot_leds, (22, 83, 102), 15),
                            pattern3(self.tot_leds, (0, 49, 133), 16),
                            pattern3(self.tot_leds, (47, 0, 255), 9),
                            pattern3(self.tot_leds, (0, 26, 74), 12),
                            pattern3(self.tot_leds, (20, 26, 74), 15)]
        else:  # If we dialed the black hole!
            pos_patterns = [pattern3(self.tot_leds, (255, 10, 59), 10),
                            pattern3(self.tot_leds, (247, 64, 95), 11),
                            pattern3(self.tot_leds, (102, 22, 35), 15),
                            pattern3(self.tot_leds, (133, 0, 22), 16),
                            pattern3(self.tot_leds, (255, 0, 85), 9),
                            pattern3(self.tot_leds, (74, 0, 15), 12)]
        return pos_patterns

    @staticmethod
    def pattern_off(number_of_leds):
        """
        This helper method creates an empty pattern (no leds active)
        :param number_of_leds: the number of leds in the wormhole strip
        :return: the pattern is returned as a list
        """
        off_pattern = []
        for index in range(number_of_leds): # pylint: disable=unused-variable
            off_pattern.append((0, 0, 0))
        return off_pattern

    @staticmethod
    def set_wormhole_pattern(pixels, pattern):
        """
        This method sets the pattern on the led strip, and displays it. No fading!
        pixels: The pixel object where to set the pattern. eg self.pixels
        :return: The pattern is returned as a string. (Am i sure it's not a list? Is this a typo?)
        """
        for led in enumerate(pattern):
            pixels[led] = pattern[led]
        pixels.show()
        return pattern

    def open_wormhole(self):
        """
        Method for opening the wormhole. For some reason i did not use the fade_transition function here..
        :return: Nothing is returned.
        """
        self.audio.sound_start('wormhole_open')  # Open wormhole audio
        for i in range(20):
            self.pixels.fill(((i // 2) * 2, i * 2, i * 2))
            self.pixels.show()
        sleep(0.5)
        for i in range(20, 128):
            self.pixels.fill(((i // 2) * 2, i * 2, i * 2))
            self.pixels.show()
        for i in range(255, 50, -2):
            self.pixels.fill((i // 2, i, i))
            self.pixels.show()
        sleep(0.3)

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

        no_pattern = self.pattern_off(self.tot_leds)

        self.stargate.wormhole = True  # temporarily to be able to use the fade_transition function
        self.fade_transition(pattern_blue(self.tot_leds))
        self.audio.sound_start('wormhole_close')  # Play the close wormhole audio
        sleep(self.wormhole_close_audio_headstart)
        self.fade_transition(no_pattern)

        # Reset some state variables
        self.stargate.wormhole_max_time = self.wormhole_max_time_default # Reset the variable
        self.stargate.audio_clip_wait_time = self.audio_clip_wait_time_default # Reset the variable
        self.stargate.wormhole = False  # Put it back the way it should be.

    def rotate_pattern(self, pattern=None, direction='ccw', speed=0, revolutions=1):
        """
        This functions spins a led pattern along the led strip.
        :param pattern: The pattern as a list. (this is optional) If left blank, we try to rotate the current pattern on the led strip.
        :param direction: The direction as a string, either cw og ccw.
        :param speed: the speed as a number. 0 is fastest, and higher is slow. eg, speed=1 (1 - 10 seems as good speeds)
        :param revolutions: The number of rounds to turn the pattern. 1 round is one whole revolution.
        :return: Noting is returned
        """
        ### Determine what pattern to spin ###
        ## convert NeoPixel object to list ###
        if pattern is None:
            pix = self.pixels
            current_pattern = []
            for led in pix:
                current_pattern.append(led)
        else:
            current_pattern = pattern

        ### direction ###
        rot_direction = -1
        if direction == 'cw':
            rot_direction = 1

        ### Rotate the pattern ###
        for revolution in range(revolutions): # pylint: disable=unused-variable
            for rotate in range(len(current_pattern)): # pylint: disable=unused-variable
                if not self.stargate.wormhole:  # if the wormhole is cancelled
                    return  # this exits the whole for loop, even if nested.
                current_pattern = [current_pattern[(i + rot_direction) % len(current_pattern)]
                                   for i, x in enumerate(current_pattern)]
                self.set_wormhole_pattern(self.pixels, current_pattern)
                sleep(speed / 100)

    def fade_transition(self, new_pattern):
        """
        This functions tries to fade the existing pattern over to the new_pattern. The new patterns are lists of tuples for each led.
        :new_pattern: This is the new pattern to match, as a list
        """
        pix = self.pixels  # these are the current pixels from the strip as neopixel object.

        def create_tween_pattern(current, new):
            """
            This function takes two pattern lists, and creates a tween pattern list one step faded towards the new list.
            :param current: the current_list as is on the led strip
            :param new: the new list to fade towards
            :return: a new tween list is returned.
            """
            in_between_pattern = []
            for i in enumerate(new):  # For the length of the new pattern list
                # The two leds to gradually match.
                current_led = current[i]
                new_led = new[i]

                # The current r,g and b's
                red = current_led[0]
                green = current_led[1]
                blue = current_led[2]

                ## increment/decrement the r
                if current_led[0] > new_led[0]:
                    red = current_led[0] - 1
                elif current_led[0] < new_led[0]:
                    red = current_led[0] + 1
                ## increment/decrement the g
                if current_led[1] > new_led[1]:
                    green = current_led[1] - 1
                elif current_led[1] < new_led[1]:
                    green = current_led[1] + 1
                ## increment/decrement the b
                if current_led[2] > new_led[2]:
                    blue = current_led[2] - 1
                elif current_led[2] < new_led[2]:
                    blue = current_led[2] + 1
                # print ((r,g,b))
                in_between_pattern.append((red, green, blue))
            return in_between_pattern

        ## convert NeoPixel object to list ###
        current_pattern = []
        for led in pix:
            current_pattern.append(led)

        ## These are the two lists we are working with.
        # print(current_pattern)
        # print(new_pattern)
        while current_pattern != new_pattern and self.stargate.wormhole:
            tween_pattern = create_tween_pattern(current_pattern, new_pattern)
            current_pattern = tween_pattern
            self.set_wormhole_pattern(self.pixels, tween_pattern)

    def sweep_transition(self, new_pattern):
        """
        This functions transitions one pattern to another with a sweeping motion.
        :param new_pattern:
        :return: Noting is returned
        """
        pix = self.pixels
        ## convert NeoPixel object to list ###
        current_pattern = []
        for led in pix:
            current_pattern.append(led)

        # random direction
        directions = ['forward', 'backwards']
        direction = choice(directions)
        if direction == 'backwards':
            for led in reversed(range(self.tot_leds)):
                current_pattern[led] = new_pattern[led]
                self.set_wormhole_pattern(self.pixels, current_pattern)
        else:
            for led in range(self.tot_leds):
                current_pattern[led] = new_pattern[led]
                self.set_wormhole_pattern(self.pixels, current_pattern)

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
        ## Lists of possible transition methods and directions
        possible_transitions = ['fade', 'sweep']
        possible_directions = ['cw', 'ccw']

        # Open The wormhole
        self.log.log('Opening Wormhole!')
        self.open_wormhole()

        # this will play the worm hole active audio. It lasts about 4min 22sec. It is deliberately not looping or restarting.
        self.audio.sound_start('wormhole_established')

        self.open_time = time()
        random_audio_start_time = time()

        # If we dialed the black hole planet, change some variables
        if self.stargate.black_hole:  # If we dialed the black hole.
            possible_patterns = self.possible_wormholes(black_hole=True)
            self.wormhole_max_time = self.wormhole_max_time_blackhole * 60  # Make it 10 years...
            self.audio_clip_wait_time = self.audio_clip_wait_time_blackhole
            audio_group = "audio_clips/black_hole"
        else:
            # If we did not dial the black hole planet
            audio_group = "audio_clips"
            possible_patterns = self.possible_wormholes(black_hole=False)

        # Keep the wormhole open
        while self.stargate.wormhole and self.get_time_remaining() > 0:  # as long as stargate.wormhole, but for less time than the wormhole_max_time.

            # TODO: These take a long time, and as a result we don't have tight timing
            # on wormhole close/timeout, and the random clips.
            #    Maybe the Neopixel stuff should run in it's own thread?

            # random transition functions
            transition = choice(possible_transitions)
            if transition == 'fade':
                self.fade_transition(choice(possible_patterns))  # Transitions between patterns
            else:
                self.sweep_transition(choice(possible_patterns))  # Transitions between patterns
            self.rotate_pattern(direction=choice(possible_directions), speed=randint(1, 10), revolutions=randint(1, 3))  # rotates the pattern.

            # Play random audio clips
            if (time() - random_audio_start_time) > self.audio_clip_wait_time:  # If there has been "silence" for more than audio_clip_wait_time
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
        self.stargate.wormhole = False # The close_wormhole method also does this.. shouldn't be needed.
        self.log.log(f'Disengaged Wormhole after {timedelta(seconds=int(time() - self.open_time))}')
        self.open_time = None
