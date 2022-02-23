from time import sleep
from random import choice, randint
from wormhole_pattern_manager import WormholePatternManager

class WormholeAnimationManager:

    def __init__(self, stargate):
        self.stargate = stargate

        # We'll need to call WormholeAnimationManager.after_init() after the Wormhole object is initialized
        # But initialize the class variables here
        self.wh_manager = None
        self.tot_leds = None
        self.pixels = None
        self.pattern_manager = None

    def after_init(self, wh_manager):
        self.wh_manager = wh_manager
        self.tot_leds = self.wh_manager.tot_leds
        self.pixels = self.wh_manager.pixels
        self.pattern_manager = WormholePatternManager(self.tot_leds)
        self.clear_wormhole() # Turn off all the LEDs

    def animate_kawoosh(self):
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

    def set_wormhole_pattern(self, pattern):
        """
        This method sets the pattern on the led strip, and displays it. No fading!
        pixels: The pixel object where to set the pattern. eg self.pixels
        :return: The pattern is returned as a string. (Am i sure it's not a list? Is this a typo?)
        """
        for index, led_state in enumerate(pattern):
            self.pixels[index] = led_state
        self.pixels.show()
        return pattern

    def clear_wormhole(self):
        """
        This method simply clears the wormhole or turns off all the leds.
        :return: Nothing is returned.
        """
        pattern = self.pattern_manager.pattern_off()
        self.set_wormhole_pattern(pattern)

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
                if not self.stargate.wormhole_active:  # if the wormhole is cancelled
                    return  # this exits the whole for loop, even if nested.
                current_pattern = [current_pattern[(i + rot_direction) % len(current_pattern)]
                                   for i, x in enumerate(current_pattern)]
                self.set_wormhole_pattern(current_pattern)
                sleep(speed / 100)

    def fade_transition(self, new_pattern):
        """
        This functions tries to fade the existing pattern over to the new_pattern. The new patterns are lists of tuples for each led.
        :new_pattern: This is the new pattern to match, as a list
        """
        pix = self.pixels  # these are the current pixels from the strip as neopixel object.

        def create_tween_pattern(current_pattern, new_pattern):
            """
            This function takes two pattern lists, and creates a tween pattern list one step faded towards the new list.
            :param current: the current_list as is on the led strip
            :param new: the new list to fade towards
            :return: a new tween list is returned.
            """
            tween_pattern = []

            # For the length of the new pattern list
            for index, new_led in enumerate(new_pattern):

                # Get the current LED's color tuple, to gradually match.
                current_led = current_pattern[index]
                red = current_led[0]
                green = current_led[1]
                blue = current_led[2]

                ## increment/decrement the red
                if current_led[0] > new_led[0]:
                    red = current_led[0] - 1
                elif current_led[0] < new_led[0]:
                    red = current_led[0] + 1
                ## increment/decrement the green
                if current_led[1] > new_led[1]:
                    green = current_led[1] - 1
                elif current_led[1] < new_led[1]:
                    green = current_led[1] + 1
                ## increment/decrement the blue
                if current_led[2] > new_led[2]:
                    blue = current_led[2] - 1
                elif current_led[2] < new_led[2]:
                    blue = current_led[2] + 1
                # print ((r,g,b))
                tween_pattern.append((red, green, blue))
            return tween_pattern

        ## convert NeoPixel object to list ###
        current_pattern = []
        for led in pix:
            current_pattern.append(led)

        ## These are the two lists we are working with.
        # print(current_pattern)
        # print(new_pattern)
        while current_pattern != new_pattern and self.stargate.wormhole_active:
            tween_pattern = create_tween_pattern(current_pattern, new_pattern)
            current_pattern = tween_pattern
            self.set_wormhole_pattern(tween_pattern)

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
                self.set_wormhole_pattern(current_pattern)
        else:
            for led in range(self.tot_leds):
                current_pattern[led] = new_pattern[led]
                self.set_wormhole_pattern(current_pattern)

    def do_random_transitions(self, is_black_hole=False):
        ## Lists of possible transition methods and directions
        possible_transitions = ['fade', 'sweep']
        possible_directions = ['cw', 'ccw']
        possible_patterns = self.pattern_manager.get_patterns(is_black_hole)

        transition = choice(possible_transitions)
        if transition == 'fade':
            self.fade_transition(choice(possible_patterns))  # Transitions between patterns
        else:
            self.sweep_transition(choice(possible_patterns))  # Transitions between patterns
        self.rotate_pattern(direction=choice(possible_directions), speed=randint(1, 10), revolutions=randint(1, 3))  # rotates the pattern.
