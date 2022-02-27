#!/usr/bin/env python3

import time
import struct
from smbus import SMBus #pylint: disable=import-error

class LEDDriver:
    def __init__(self, cfg, log):

        self.log = log
        self.cfg = cfg

        self.log.log( "Initializing LED Driver" )

        # Configure
        # TODO: Move these to config
        self.i2c_bus_id = 1
        self.i2c_slave_address = 0x38 # Because 38 minutes!

        # Define commands
        self.COMMAND_SET_CHEVRON =              10 # pylint: disable=invalid-name
        self.COMMAND_CLEAR_CHEVRON =            11 # pylint: disable=invalid-name
        self.COMMAND_SET_SYMBOL_IN_POSITION =   12 # pylint: disable=invalid-name
        self.COMMAND_SET_BITMAP_IN_POSITION =   15 # pylint: disable=invalid-name
        self.COMMAND_CLEAR_SYMBOL_IN_POSITION = 13 # pylint: disable=invalid-name
        self.COMMAND_CLEAR_ALL =                14 # pylint: disable=invalid-name
        self.COMMAND_SET_PIXEL_RAW =            16 # pylint: disable=invalid-name
        self.COMMAND_CLEAR_PIXEL_RAW =          17 # pylint: disable=invalid-name
        self.COMMAND_CLEAR_ALL_CHEVRONS =       18 # pylint: disable=invalid-name

        # ======================================================

        self.i2c = SMBus(self.i2c_bus_id) # Initialize the I2C Bus

        self.clear_all() # Clear all the pixels on init
        time.sleep(0.5)

        # The different modes for lighting a chevron - pass one of these to set_chevron()
        self.CHEVRON_SEGMENT_OFF         = 0 # pylint: disable=invalid-name
        self.CHEVRON_SEGMENT_V_ONLY      = 1 # pylint: disable=invalid-name
        self.CHEVRON_SEGMENT_LENS_ONLY   = 2 # pylint: disable=invalid-name
        self.CHEVRON_SEGMENT_ALL         = 3 # pylint: disable=invalid-name

        # Used to lookup pretty name for debug. Keep in same order as above
        self.chevron_segment_enum = [
            "Off",
            "V ONLY",
            "LENS ONLY",
            "ALL"
        ]

        self.log.log( "LED Driver is Ready!" )

    # ++++++++++++++++++++++++++++++++++++++++++

    def get_segment_name(self, segment):
        return self.chevron_segment_enum[segment]

    def set_chevron( self, pos, red_color, green_color, blue_color, segment ):
        self.log.log(f"Turning Chevron {pos} ON ({red_color}, {green_color}, {blue_color}, Segment: {self.get_segment_name(segment)})")
        message = [ (pos-1), red_color, green_color, blue_color, segment ]
        self.__write_message(self.COMMAND_SET_CHEVRON, message)

    def clear_chevron(self, pos):
        self.log.log(f"Turning Chevron {pos} OFF")
        message = [ pos ]
        self.__write_message(self.COMMAND_CLEAR_CHEVRON, message)

    def clear_all_chevrons(self):
        self.log.log(f"Turning ALL Chevrons {pos} OFF")
        self.__write_message(self.COMMAND_CLEAR_CHEVRON, [])

    def display_symbol_in_position( self, symbol, pos, red_color, green_color, blue_color ):
        self.log.log(f"Displaying pre-saved Symbol {symbol} in Position {pos} ({red_color}, {green_color}, {blue_color})")

        message = [ symbol, pos, red_color, green_color, blue_color ]
        self.__write_message(self.COMMAND_SET_SYMBOL_IN_POSITION, message)

    def display_bitmap_in_position( self, bitmap, pos, red_color, green_color, blue_color ):
        self.log.log(f"Displaying Bitmap {hex(bitmap)} in position {pos} ({red_color}, {green_color}, {blue_color})")

        # Split the 32-bit unsigned long into 4 bytes for transmission
        bitmap_buffer = struct.unpack('4B', struct.pack('>I', bitmap))

        message = [ bitmap_buffer[0], bitmap_buffer[1], bitmap_buffer[2], bitmap_buffer[3],
            pos, red_color, green_color, blue_color ]
        self.__write_message(self.COMMAND_SET_BITMAP_IN_POSITION, message)

    def clear_symbol_in_position( self, pos ):
        self.log.log(f"Clearing symbol position {pos}")
        message = [ pos ]
        self.__write_message(self.COMMAND_CLEAR_SYMBOL_IN_POSITION, message)

    def clear_all(self):
        self.log.log("Clearing All LEDs")
        self.__write_message(self.COMMAND_CLEAR_ALL, [] )

    def set_pixel_raw( self, pixel, red_color, green_color, blue_color ):
        self.log.log(f"Setting pixel {pixel} to ({red_color}, {blue_color}, {green_color})")

        # Split the 32-bit unsigned long into 4 bytes for transmission
        pixel_buffer = struct.unpack('4B', struct.pack('>I', pixel))

        message = [ pixel_buffer[0], pixel_buffer[1], pixel_buffer[2], pixel_buffer[3],
            red_color, green_color, blue_color ]
        self.__write_message(self.COMMAND_SET_PIXEL_RAW, message)


    def clear_pixel_raw( self, pixel ):
        self.log.log(f"Clearing pixel {pixel}")

        # Split the 32-bit unsigned long into 4 bytes for transmission
        pixel_buffer = struct.unpack('4B', struct.pack('>I', pixel))

        message = [ pixel_buffer[0], pixel_buffer[1], pixel_buffer[2], pixel_buffer[3] ]
        self.__write_message(self.COMMAND_CLEAR_PIXEL_RAW, message)

    def test(self, repeat = True):
        self.log.log("Starting test sequence")
        while True:

            self.set_chevron( 0, 255, 0, 0, self.CHEVRON_SEGMENT_ALL ) # Chevron 0, red
            time.sleep(0.5)

            self.clear_chevron( 0 ) # Clear Chevron 0
            time.sleep(0.5)

            self.display_symbol_in_position( 1, 1, 0, 255, 0 ) # symbol 1 in position 1, green
            time.sleep(0.5)

            self.clear_symbol_in_position ( 1 ) # Clear position 1
            time.sleep(0.5)

            self.display_bitmap_in_position( 0x900009, 1, 0, 0, 255 ) # Position 1, four corners, blue
            time.sleep(0.5)

            self.clear_symbol_in_position ( 1 ) # Clear position 1
            time.sleep(0.5)

            self.set_pixel_raw( 49, 255, 255, 255) # 50th pixel, ON white
            time.sleep(0.5)

            self.clear_pixel_raw( 49 ) # 50th pixel, off
            time.sleep(0.5)

            if not repeat:
                return

    # ++++++++++++++++++++++++++++++++++++++++++

    def __write_message(self, command, message, retries_remaining = 5):
        try:
            self.i2c.write_i2c_block_data( self.i2c_slave_address, command, message)
        except (TypeError, ValueError, IOError):
            self.log.log("Failed to write...retrying")
            self.__write_message(command, message, retries_remaining-1)
