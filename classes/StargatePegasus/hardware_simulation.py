#!/usr/bin/env python3

import time

class LEDDriverSim():
    def __init__(self, app):
        self.log = app.log

        self.log.log( "Initializing Simulated LED Driver" )

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

        self.log.log( "Simulated LED Driver is Ready!" )

    # ++++++++++++++++++++++++++++++++++++++++++
    def get_segment_name(self, segment):
        return self.chevron_segment_enum[segment]

    def set_chevron( self, pos, red_color, green_color, blue_color, segment ):
        self.log.log(f"Simulated: Turning Chevron {pos} ON ({red_color}, {green_color}, {blue_color}, Segment: {self.get_segment_name(segment)})")

    def clear_chevron(self, pos):
        self.log.log(f"Simulated: Turning Chevron {pos} OFF")

    def display_symbol_in_position( self, symbol, pos, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Displaying pre-saved Symbol {symbol} in Position {pos} ({red_color}, {green_color}, {blue_color})")

    def display_bitmap_in_position( self, bitmap, pos, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Displaying Bitmap {hex(bitmap)} in position {pos} ({red_color}, {green_color}, {blue_color})")

    def clear_symbol_in_position( self, pos ):
        self.log.log(f"Simulated: Clearing symbol position {pos}")

    def clear_all(self):
        self.log.log("Simulated: Clearing All LEDs")

    def set_pixel_raw( self, pixel, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Setting pixel {pixel} to ({red_color}, {blue_color}, {green_color})")

    def clear_pixel_raw( self, pixel ):
        self.log.log(f"Simulated: Clearing pixel {pixel}")

    def test(self, repeat = True):
        self.log.log("Simulated: Starting test sequence")
        while True:

            self.set_chevron( 0, 255, 0, 0 ) # Chevron 0, red
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
