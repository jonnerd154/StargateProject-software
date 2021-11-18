#!/usr/bin/python3
import sys
import os
sys.path.append('classes')
sys.path.append('config')

from stargate_config import StargateConfig
from ancients_log_book import AncientsLogBook
from software_update import SoftwareUpdate
from stargate_audio import StargateAudio

from time import sleep
from HardwareDetector import HardwareDetector
from chevrons import ChevronManager

from adafruit_motorkit import MotorKit
from adafruit_motor import stepper as stp
import neopixel, board

### Load our config file
cfg = StargateConfig()

### Setup the logger
log = AncientsLogBook()

### Initialize the audio stuffs
audio = StargateAudio(log)
audio.set_correct_audio_output_device()


log.log('Gate Hardware Test: Starting.')

# ########### WORMHOLE NEOPIXEL TESTS ###############

neoPin = board.D12  # The standard data pin is board.D18
tot_leds = 122
pixels = neopixel.NeoPixel(neoPin, tot_leds, auto_write=False, brightness=0.61)

log.log("Testing wormhole neopixels. Press ctrl+c to continue to next test.")
while(True):
    try:
        for i in range(20):
            pixels.fill(((i // 2) * 2, i * 2, i * 2))
            pixels.show()
        sleep(0.5)
        for i in range(20, 128):
            pixels.fill(((i // 2) * 2, i * 2, i * 2))
            pixels.show()
        for i in range(255, 50, -2):
            pixels.fill((i // 2, i, i))
            pixels.show()
        sleep(0.3)
    except KeyboardInterrupt:
        off_pattern = []
        for i in range(tot_leds):
            pixels.fill((0,0,0))
            pixels.show()
        break

# #### Motor Hardware Detection #################

hwDetector = HardwareDetector()
motorHardwareMode = hwDetector.getMotorHardwareMode()
modeName = hwDetector.getMotorHardwareModeName()
if (not modeName):
    log.log("Warning: No supported motor hardware controllers detected")

else:
    log.log("Motor Hardware FOUND: {}".format(modeName))

# ########### SYMBOL RING MOTOR TESTS ###############
#
# total_steps = 1250
# stepper = None

# if motorHardwareMode > 0:
#     stepper = MotorKit().stepper1
#     sleep(0.4)
#     stepper.release()
#
# # move a short distance clockwise
# direct = stp.FORWARD
# speed = 0.01
# input("Moving the ring clockwise. Press enter to start.")
# while(True):
#     try:
#         for i in range(1,100):
#             stepper.onestep(direction=direct, style=stp.DOUBLE) + 8 # this line moves the motor.
#             sleep(speed)
#         sleep(0.4)
#         stepper.release()
#         inputStr = input("Press Enter to move clockwise again. Press 'n' and hit enter to move to the next test.")
#         if inputStr == "n":
#             break
#         else:
#             continue
#
#     except KeyboardInterrupt:
#         break
#
# direct = stp.BACKWARD
# input("Moving the ring counter-clockwise. Press enter to start.")
# while(True):
#     try:
#         for i in range(1,100):
#             stepper.onestep(direction=direct, style=stp.DOUBLE) + 8 # this line moves the motor.
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Press Enter to move counterclockwise again. Press 'n' and hit enter to move to the next test.")
#         if inputStr == "n":
#             break
#         else:
#             continue
#
#     except KeyboardInterrupt:
#         break
#
# sleep(0.4)
# stepper.release()
#
# while(True):
#     direct = stp.FORWARD
#     input("CALIBRATION: The ring is unlocked. Gently move the \"Home\" symbol into the top chevron. Press enter when done.")
#
#     # Save the current position in the file
#
#     try:
#         for i in range(1,total_steps):
#             stepper.onestep(direction=direct, style=stp.DOUBLE)
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Is the \"Home\" symbol at the top again? (y)es or (n)o")
#         if inputStr == "y":
#             break
#         else:
#             continue
#
#     except KeyboardInterrupt:
#         break
#
# while(True):
#     direct = stp.BACKWARD
#
#     # Save the current position in the file
#
#     try:
#         for i in range(1,total_steps):
#             stepper.onestep(direction=direct, style=stp.DOUBLE)
#             sleep(speed)
#         stepper.release()
#         inputStr = input("Is the \"Home\" symbol at the top again? (y)es or (n)o")
#         if inputStr == "y":
#             break
#         else:
#             continue
#
#     except KeyboardInterrupt:
#         break
#
# sleep(0.4)
# stepper.release()

# ########### CHEVRON TESTS ###############

# Load the chevron configuration and initialize their objects
chevrons = ChevronManager(log, cfg)
log.log( "Testing Chevron lights and motors. Motor should move inward, the light should turn on, then the motor should move outward. ")
for i in range(1,8):
    log.log("Testing Chevron {}.".format(i))
    chevrons.get(i).on()
    sleep(1)

# ##########################################



# Exit
log.log('Gate Hardware Test: Done.')
