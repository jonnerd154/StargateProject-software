import os
from time import sleep
from serial.serialutil import SerialException
import StargateCmdMessenger

class Dialer: # pylint: disable=too-few-public-methods

    def __init__(self, stargate):

        self.log = stargate.log
        self.cfg = stargate.cfg

        # Retrieve the configurations
        self.dhd_port = self.cfg.get("dhd_serial_port")
        self.dhd_serial_baud_rate = self.cfg.get("dhd_serial_baud_rate")
        self.dhd_brightness_center = self.cfg.get("dhd_brightness_center")
        self.dhd_brightness_symbols = self.cfg.get("dhd_brightness_symbols")
        self.dhd_enable = self.cfg.get("dhd_enable")
        self.dhd_color_center = [
            self.cfg.get("dhd_color_center_red"),
            self.cfg.get("dhd_color_center_green"),
            self.cfg.get("dhd_color_center_blue")
        ]

        self.dhd_color_symbols = [
            self.cfg.get("dhd_color_symbols_red"),
            self.cfg.get("dhd_color_symbols_green"),
            self.cfg.get("dhd_color_symbols_blue")
        ]

        self.hardware = None
        self.type = None

        self._connect_dialer()

    def _connect_dialer(self):
        # Detect if we have a DHD connected, else use the keyboard
        try:
            # If The DHD is disabled, raise an exception to jump to the except block and use KeyboardMode
            if not self.dhd_enable:
                raise AttributeError

            self.hardware = self._connect_dhd()
            self.type = "DHDv2"
        except SerialException:
            self.log.log('No DHD found or DHD is disabled. Switching to keyboard mode')
            self.hardware = KeyboardMode()
            self.type = "Keyboard"

    def _connect_dhd(self):
        try:
            # Get a Semaphore lock on the parent process so when the PyCmdMessenger class
            # prints to STDOUT, it doesn't step on STDOUT from other threads
            ### Connect to the DHD object. Will throw exception if not present
            dhd = DHDv2(self.dhd_port, self.dhd_serial_baud_rate, self.log)
            self.log.log('DHDv2 Found. Connected.')
        except SerialException: # pylint: disable=try-except-raise
            raise

        # Configure the DHD
        dhd.set_brightness_center(self.dhd_brightness_center)
        dhd.set_brightness_symbols(self.dhd_brightness_symbols)
        dhd.set_color_center(self.dhd_color_center)
        dhd.set_color_symbols(self.dhd_color_symbols)

        # Blink the middle button to signal the DHD is ready
        dhd.set_pixel(0, 255, 255, 255)
        dhd.latch()
        sleep(0.5)
        dhd.set_all_pixels_to_color(0, 0, 0)
        dhd.latch()

        return dhd

class DHDv2:

    def __init__(self, port, baud_rate, log):
        # Initialize an ArduinoBoard instance.
        self.board = StargateCmdMessenger.ArduinoBoard(port, baud_rate=baud_rate, log=log)

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

        self.color_symbols = None
        self.color_center = None

        # Initialize the messenger
        self.c = StargateCmdMessenger.CmdMessenger(self.board, self.commands) # pylint: disable=invalid-name

    def get_firmware_version(self):
        self.c.send("get_fw_version")
        return self.c.receive()[1][0]

    def get_hardware_version(self):
        self.c.send("get_hw_version")
        return self.c.receive()[1][0]

    def get_identifier_string(self):
        self.c.send("get_identifier")
        return self.c.receive()[1][0]

    def get_pixel_color_tuple(self, pixel_index):
        self.c.send("get_pixel_color", pixel_index)
        return self.c.receive()[1]

    def get_pixel_count(self):
        self.c.send("get_pixel_count")
        return self.c.receive()[1][0]

    def set_brightness_symbols(self, brightness):
        self.c.send("set_brightness_symbols", brightness)
        return True

    def set_brightness_center(self, brightness):
        self.c.send("set_brightness_center", brightness)
        return True

    def set_all_pixels_to_color(self, red, green, blue):
        self.c.send("set_all", red, green, blue)
        return True

    def set_pixel(self, pixel_index, red, green, blue):
        symbol_number_to_dhd_light_map = {0: 0, 1: 34, 2: 2, 3: 21, 4: 20, 5: 36, 6: 29, 7: 31, 8: 18, 9: 37,
                                          10: 10, 11: 23, 12: 25, 14: 4, 15: 15, 16: 12, 17: 3, 18: 5, 19: 33,
                                          20: 38, 21: 22, 22: 32, 23: 6, 24: 30, 25: 1, 26: 7, 27: 17, 28: 11, 29: 28,
                                          30: 13, 31: 16, 32: 35, 33: 9, 34: 26, 35: 14, 36: 19, 37: 24, 38: 27, 39: 8}
        self.c.send("set_pixel", symbol_number_to_dhd_light_map[pixel_index], red, green, blue)
        return True

    def set_pixel_use_led_id(self, pixel_index, red, green, blue):
        self.c.send("set_pixel", pixel_index, red, green, blue)
        return True

    def clear_all_pixels(self):
        self.c.send("clear_all")
        return True

    def clear_pixel(self, pixel_index):
        self.c.send("clear_pixel", pixel_index)
        return True

    def latch(self):
        self.c.send("latch")
        return True

    def clear_lights(self):
        self.set_all_pixels_to_color(0, 0, 0) # All Off
        self.latch()

    def set_center_on( self ):
        self.set_pixel(0, self.color_center[0], self.color_center[1], self.color_center[2]) # LED 0, Pure red.
        self.latch()

    def set_symbol_on( self, symbol_number ):
        self.set_pixel(symbol_number, self.color_symbols[0], self.color_symbols[1], self.color_symbols[2])
        self.latch()

    def set_color_center(self, color_tuple):
        self.color_center = color_tuple

    def set_color_symbols(self, color_tuple):
        self.color_symbols = color_tuple

    @staticmethod
    def get_dhd_port():
        """
        This is a simple helper function to help locate the port for the DHD
        :return: The file path for the DHD is returned. If it is not found, returns None.
        """
        # A list for places to check for the DHD
        possible_files = ["/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00", "/dev/ttyACM0", "/dev/ttyACM1"]

        # Run through the list and check if the file exists.
        for file in possible_files:
            # If the file exists, return the path and end the function.
            if os.path.exists(file):
                return file

        # If the DHD is not detected
        return None


class KeyboardMode:
    """
    This is just a fallback class that disables all the DHD LED functions in case the DHD is not present. You can use a regular keyboard instead.
    To dial Aphopis's base, just hit cFX1K98A on your keyboard.
    """

    def __init__(self):
        pass

    @staticmethod
    def get_firmware_version():
        pass

    @staticmethod
    def get_hardware_version():
        pass

    @staticmethod
    def get_identifier_string():
        pass

    @staticmethod
    def get_pixel_color_tuple(pixel_index):
        pass

    @staticmethod
    def get_pixel_count():
        pass

    @staticmethod
    def set_brightness_symbols(brightness):
        pass

    @staticmethod
    def set_brightness_center(brightness):
        pass

    @staticmethod
    def set_all_pixels_to_color(red, green, blue):
        pass

    @staticmethod
    def set_pixel(pixel_index, red, green, blue): # pylint: disable=unused-argument
        # pylint: disable-next=unused-variable
        symbol_number_to_dhd_light_map = {0: 0, 1: 34, 2: 2, 3: 21, 4: 20, 5: 36, 6: 29, 7: 31, 8: 18, 9: 37,
                                          10: 10, 11: 23, 12: 25, 14: 4, 15: 15, 16: 12, 17: 3, 18: 5, 19: 33,
                                          20: 38, 21: 22, 22: 32, 23: 6, 24: 30, 25: 1, 26: 7, 27: 17, 28: 11, 29: 28,
                                          30: 13, 31: 16, 32: 35, 33: 9, 34: 26, 35: 14, 36: 19, 37: 24, 38: 27, 39: 8}
        # TODO: initialize dummy data instead

    @staticmethod
    def set_pixel_use_led_id(pixel_index, red, green, blue):
        pass

    @staticmethod
    def clear_all_pixels():
        pass

    @staticmethod
    def clear_pixel(pixel_index):
        pass

    @staticmethod
    def latch():
        pass

    @staticmethod
    def clear_lights():
        pass

    @staticmethod
    def set_center_on():
        pass

    @staticmethod
    def set_symbol_on(symbol_number):
        pass

    @staticmethod
    def set_color_center(color_tuple):
        pass

    @staticmethod
    def set_color_symbols(color_tuple):
        pass
