class WormholePatternManager:

    def __init__(self, tot_leds):
        self.tot_leds = tot_leds

        self.standard_patterns = []
        self.black_hole_patterns = []

        self.init_patterns()

    def pattern_off(self):
        """
        This helper method creates an empty pattern (no leds active)
        :return: the pattern is returned as a list
        """
        off_pattern = []
        for index in range(self.tot_leds): # pylint: disable=unused-variable
            off_pattern.append((0, 0, 0))
        return off_pattern

    def pattern1(self, color1, color2):
        """
        This method creates the wormhole pattern1
        :param color1: the first color as a tuple of rgb values, eg: (26, 56, 105)
        :param color2: the second color as a tuple of rgb values, eg: (26, 56, 105)
        :return: A list containing the led colors for the wormhole is returned.
        """
        pattern = []
        for led in range(self.tot_leds):
            pattern.append(color1)
        for led in range(0, self.tot_leds, 5):
            pattern[led] = color2
            pattern[led - 1] = color2
        return pattern

    def pattern2(self, base_color, size):
        """
        This method creates the wormhole pattern2
        :param base_color: The base color for the pattern
        :param size: the size of the spacing in the pattern. Should be an int between 5, and 15 should be fine.
        :return: A list is returned.
        """
        pattern = []
        second_color = ((base_color[0] + 5) % 255, (base_color[1] + 5) % 255, (base_color[2] - 190) % 255)
        third_color = ((base_color[0] + 5) % 255, (base_color[1] + 200) % 255, (base_color[2] // 2) % 255)
        for led in range(self.tot_leds):
            pattern.append(base_color)
        for led in range(0, self.tot_leds, self.tot_leds // size):
            pattern[led] = second_color
            pattern[(led + 1) % self.tot_leds] = second_color
            pattern[(led - 1) % self.tot_leds] = second_color
            pattern[(led + 2) % self.tot_leds] = third_color
            pattern[(led - 2) % self.tot_leds] = third_color
        return pattern

    def pattern3( self, base_color, size):
        """
        This method creates the wormhole pattern3
        :param base_color: The base color for the pattern
        :param size: the size of the spacing in the pattern. 10 seems fine.
        :return: A list is returned.
        """
        pattern = []
        for led in range(self.tot_leds):
            pattern.append(base_color)
        for led in range(0, self.tot_leds, size):
            # pattern[led] = (base_color[0//2], base_color[1]//2, base_color[2]//2)
            pattern[(led - 1) % self.tot_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
            pattern[(led - 2) % self.tot_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
            pattern[(led - 3) % self.tot_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
            pattern[(led - 4) % self.tot_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
            pattern[(led - 5) % self.tot_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
            pattern[(led - 6) % self.tot_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
            pattern[(led - 7) % self.tot_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
            pattern[led] = base_color
            pattern[(led + 1) % self.tot_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
            pattern[(led + 2) % self.tot_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
            pattern[(led + 3) % self.tot_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
            pattern[(led + 4) % self.tot_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
            pattern[(led + 5) % self.tot_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
            pattern[(led + 6) % self.tot_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
            pattern[(led + 7) % self.tot_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
        return pattern

    def get_patterns(self, black_hole=False):
        if not black_hole:
            return self.standard_patterns
        return self.black_hole_patterns

    def init_patterns(self):
        #pylint: disable=too-many-function-args
        self.standard_patterns = [
                            self.pattern1((26, 56, 105), (5, 37, 247)),
                            self.pattern1((2, 172, 207), (5, 46, 250)),
                            self.pattern1((56, 25, 252), (97, 184, 255)),
                            self.pattern2((0, 0, 200), 12),
                            self.pattern2((0, 10, 255), 8),
                            self.pattern2((10, 20, 200), 15),
                            self.pattern3((10, 10, 255), 10),
                            self.pattern3((64, 229, 247), 11),
                            self.pattern3((22, 83, 102), 15),
                            self.pattern3((0, 49, 133), 16),
                            self.pattern3((47, 0, 255), 9),
                            self.pattern3((0, 26, 74), 12),
                            self.pattern3((20, 26, 74), 15)]

        self.black_hole_patterns = [
                            self.pattern3((255, 10, 59), 10),
                            self.pattern3((247, 64, 95), 11),
                            self.pattern3((102, 22, 35), 15),
                            self.pattern3((133, 0, 22), 16),
                            self.pattern3((255, 0, 85), 9),
                            self.pattern3((74, 0, 15), 12)]
