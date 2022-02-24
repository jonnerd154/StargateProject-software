#!/usr/bin/env python3

import time

class LEDDriverSim():
    def __init__(self, app):
        self.log = app.log
        self.log.log( "SIMULATED Atlantis LED Driver is Ready!" )

    # ++++++++++++++++++++++++++++++++++++++++++

    def set_chevron( self, pos, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Turning Chevron {pos} ON ({red_color}, {green_color}, {blue_color})");

    def clear_chevron(self, pos):
        self.log.log(f"Simulated: Turning Chevron {pos} OFF")

    def display_symbol_in_position( self, symbol, pos, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Displaying pre-saved Symbol {symbol} in Position {pos} ({red_color}, {green_color}, {blue_color})")

    def display_bitmap_in_position( self, bitmap, pos, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Displaying Bitmap {hex(bitmap)} in position {pos} ({red_color}, {green_color}, {blue_color})")

    def clear_symbol_in_position( self, pos ):
        self.log.log(f"Simulated: Clearing symbol position {pos}");

    def clear_all(self):
        self.log.log(f"Simulated: Clearing All LEDs");

    def set_pixel_raw( self, pixel, red_color, green_color, blue_color ):
        self.log.log(f"Simulated: Setting pixel {pixel} to ({red_color}, {blue_color}, {green_color})");

    def clear_pixel_raw( self, pixel ):
        self.log.log(f"Simulated: Clearing pixel {pixel}");

    def test(self, repeat = True):
        self.log.log("Simulated: Starting test sequence")
        while ( True ):

            self.set_chevron( 0, 255, 0, 0 ); # Chevron 0, red
            time.sleep(0.5)

            self.clear_chevron( 0 ); # Clear Chevron 0
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
