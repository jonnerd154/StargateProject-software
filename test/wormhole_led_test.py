import sys
import board
import neopixel
from time import sleep

'''

Test Script for Wormhole Neopixel LEDs

This script tests a 122-pixel long chain of LEDS, cycling between
red, green, and blue colors at a moderate brightness

TheStargateProject.com / BuildAStargate.com

'''

# --------------------------------------------

# CONFIGURATION

brightness = 10 # 0-255. Recommend not exceeding 127.
delay = 0.5     # In seconds, time to show each color

# Color tuples are ( RED, GREEN, BLUE )
# Define a list to cycle through
colors = [
  (brightness, 0, 0), # Red
  (0, brightness, 0), # Green
  (0, 0, brightness), # Blue
  (0, 0, 0)           # Off
]

pixel_order = neopixel.GRB    # Default 
#pixel_order = neopixel.GRBW  # Some SK6812

# --------------------------------------------

# Initialize the strip
pixels = neopixel.NeoPixel(board.D12, 122, pixel_order=pixel_order)

# Test until keyboard interrupt
try:
  print("Testing Neopixel strip. Press ctrl+c to stop.")
  while 1:
    for color_tuple in colors:
      pixels.fill(color_tuple)
      pixels.show()
      sleep(0.5)

except KeyboardInterrupt:
  pixels.fill((0,0,0))
  pixels.show()
  sys.exit(0)
