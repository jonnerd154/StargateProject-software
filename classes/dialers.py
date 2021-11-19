from time import sleep

class Dialer:

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg
        
        # TODO: Move to config
        self.DHD_port = "/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00"
        self.DHD_baud_rate = 115200

        self.hardware = None
        
        self._connect_dialer()
        
    def _connect_dialer(self):
        # Detect if we have a DHD connected, else use the keyboard
        try:
            self.hardware = self.connect_dhd()
        except:
            self.log.log('No DHD found, switching to keyboard mode')
            self.hardware = KeyboardMode()

    def _connect_dhd(self):
        ### Connect to the DHD object. Will throw exception if not present
        dhd = DHDv2(self.DHD_port, self.DHD_baud_rate)
        self.log.log('DHDv2 Found. Connected.')

        dhd.setBrightnessCenter(100)
        dhd.setBrightnessSymbols(3)

        # Blink the middle button to signal the DHD is ready
        dhd.setPixel(0, 255, 255, 255)
        dhd.latch()
        sleep(0.5)
        dhd.setAllPixelsToColor(0, 0, 0)
        dhd.latch()

        return dhd

class DHD:
    """
    This is the old DHD version. Not recommended. Use the new version instead.
    """
    def __init__(self):
        import adafruit_dotstar as dotstar
        import board
        self.dots = dotstar.DotStar(board.D14, board.D15, 39, brightness=0.01)
        self.center_dot = dotstar.DotStar(board.D14, board.D15, 1, brightness=0.15)

    def light_on(self, symbol_number, color):
        """
        This helper function activates the light for the dhd button of "symbol" with the "color" specified.
        :param symbol_number: The symbol number of which to control.
        :param color: The color for the led as a tuple. eg: (250, 117, 0)
        :return: nothing is returned.
        """
        symbol_number_to_dhd_light_map = {0: 0, 1: 25, 2: 19, 3: 38, 4: 20, 5: 23, 6: 30, 7: 28, 8: 3, 9: 22,
                                          10: 11, 11: 36, 12: 34, 14: 17, 15: 6, 16: 9, 17: 18, 18: 16, 19: 26,
                                          20: 21, 21: 37, 22: 27, 23: 15, 24: 29, 25: 1, 26: 14, 27: 4, 28: 10, 29: 31,
                                          30: 8, 31: 5, 32: 24, 33: 12, 34: 33, 35: 7, 36: 2, 37: 35, 38: 32, 39: 13}
        self.dots[symbol_number_to_dhd_light_map[symbol_number]] = color
    def lights_off(self):
        """
        This method turns off all dhd lights
        """
        self.dots.fill((0, 0, 0))
    def center_light_on(self):
        """
        A helper function to turn on the centre dhd light. It needs a bit more brightness than the other lights. Hence
        this extra method.
        """
        self.center_dot[0] = (255, 0, 0)

import PyCmdMessenger
from pprint import pprint

class DHDv2:

    def __init__(self, port, baud_rate):
        # Initialize an ArduinoBoard instance.
        self.board = PyCmdMessenger.ArduinoBoard(port, baud_rate=baud_rate)

        # List of command names (and formats for their associated arguments). These must
        # be in the same order as in the sketch.
        self.commands = [
            ["get_fw_version", "s"],
            ["get_hw_version", "s"],
            ["get_identifier", "s"],
            ["reset", ""],
            ["evt_error", "s"],
            ["evt_ack", ""],

            ["message_bool", "?"],
            ["message_string", "s"],
            ["message_int", "i"],
            ["message_long", "l"],
            ["message_double", "d"],
            ["message_color", "iii"],

            ["clear_all", ""],  # Turns off all pixels in the RAM buffer.
            ["clear_pixel", "i"],
            # Turns off the pixel at the provided index, in the RAM buffer. [ pixelIndex ]. Index starts at 0.
            ["set_all", "iii"],  # Sets all pixels to color provided, in the RAM buffer. [ red, green, blue ]
            ["set_pixel", "iiii"],
            # Sets pixel to color provided, in the RAM buffer.[ pixelIndex, red, green, blue ]. Index starts at 0.

            ["get_pixel_count", "i"],  # Returns the number of pixels managed by the library instance

            ["set_brightness_symbols", "i"],  # Set brightness for the symbol rings' LEDs.
            # ** Per library documentation: "Intended to be called once, in setup(),
            # to limit the current/brightness of the LEDs throughout the life of the
            # sketch. It is not intended as an animation effect itself! The operation
            # of this function is “lossy” — it modifies the current pixel data in RAM,
            # not in the show() call — in order to meet NeoPixels’ strict timing
            # requirements. Certain animation effects are better served by leaving the
            # brightness setting at the default maximum, modulating pixel brightness
            # in your own sketch logic and redrawing the full strip with setPixel()."
            ["set_brightness_center", "i"],  # Set brightness for the center LED. Call this once: cautions as above.

            ["latch", ""],  # Transmits the current pixel configuration in the RAM buffer out to the pixels
        ]

        # Initialize the messenger
        self.c = PyCmdMessenger.CmdMessenger(self.board, self.commands)

        pass

    def getFirmwareVersion(self):
        self.c.send("get_fw_version")
        return self.c.receive()[1][0]

    def getHardwareVersion(self):
        self.c.send("get_hw_version")
        return self.c.receive()[1][0]

    def getIdentifierString(self):
        self.c.send("get_identifier")
        return self.c.receive()[1][0]

    def getPixelColorTuple(self, pixelIndex):
        self.c.send("get_pixel_color", pixelIndex)
        pprint(self.c.receive())
        return self.c.receive()[1]

    def getPixelCount(self):
        self.c.send("get_pixel_count")
        return self.c.receive()[1][0]

    def setBrightnessSymbols(self, brightness):
        self.c.send("set_brightness_symbols", brightness)
        return True

    def setBrightnessCenter(self, brightness):
        self.c.send("set_brightness_center", brightness)
        return True

    def setAllPixelsToColor(self, red, green, blue):
        self.c.send("set_all", red, green, blue)
        return True

    def setPixel(self, pixelIndex, red, green, blue):
        symbol_number_to_dhd_light_map = {0: 0, 1: 34, 2: 2, 3: 21, 4: 20, 5: 36, 6: 29, 7: 31, 8: 18, 9: 37,
                                          10: 10, 11: 23, 12: 25, 14: 4, 15: 15, 16: 12, 17: 3, 18: 5, 19: 33,
                                          20: 38, 21: 22, 22: 32, 23: 6, 24: 30, 25: 1, 26: 7, 27: 17, 28: 11, 29: 28,
                                          30: 13, 31: 16, 32: 35, 33: 9, 34: 26, 35: 14, 36: 19, 37: 24, 38: 27, 39: 8}
        self.c.send("set_pixel", symbol_number_to_dhd_light_map[pixelIndex], red, green, blue)
        return True

    def setPixel_use_LED_id(self, pixelIndex, red, green, blue):
        self.c.send("set_pixel", pixelIndex, red, green, blue)
        return True

    def clearAllPixels(self):
        self.c.send("clear_all")
        return True

    def clearPixel(self, pixelIndex):
        self.c.send("clear_pixel", pixelIndex)
        return True

    def latch(self):
        self.c.send("latch")
        return True
    
    def clear_lights(self):
        self.setAllPixelsToColor(0, 0, 0)
        self.latch()

class KeyboardMode:
    """
    This is just a fallback class that disables all the DHD LED functions in case the DHD is not present. You can use a regular keyboard instead.
    To dial Aphopis's base, just hit cFX1K98A on your keyboard.
    """

    def __init__(self):
        pass

    def getFirmwareVersion(self):
        pass

    def getHardwareVersion(self):
        pass

    def getIdentifierString(self):
        pass

    def getPixelColorTuple(self, pixelIndex):
        pass

    def getPixelCount(self):
        pass

    def setBrightnessSymbols(self, brightness):
        pass

    def setBrightnessCenter(self, brightness):
        pass

    def setAllPixelsToColor(self, red, green, blue):
        pass

    def setPixel(self, pixelIndex, red, green, blue):
        symbol_number_to_dhd_light_map = {0: 0, 1: 34, 2: 2, 3: 21, 4: 20, 5: 36, 6: 29, 7: 31, 8: 18, 9: 37,
                                          10: 10, 11: 23, 12: 25, 14: 4, 15: 15, 16: 12, 17: 3, 18: 5, 19: 33,
                                          20: 38, 21: 22, 22: 32, 23: 6, 24: 30, 25: 1, 26: 7, 27: 17, 28: 11, 29: 28,
                                          30: 13, 31: 16, 32: 35, 33: 9, 34: 26, 35: 14, 36: 19, 37: 24, 38: 27, 39: 8}
        pass

    def setPixel_use_LED_id(self, pixelIndex, red, green, blue):
        pass

    def clearAllPixels(self):
        pass

    def clearPixel(self, pixelIndex):
        pass

    def latch(self):
        pass
    
    def clear_lights(self):
        pass
